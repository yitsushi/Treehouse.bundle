import re, string, urllib2, datetime, time
from config import CATEGORIES

TH_PREFIX        = '/video/treehouse'
TH_FEED_URL      = 'http://teamtreehouse.com/library/%s.rss?feed_token=%s'
CACHE_INTERVAL   = 1800
FORMATS          = ['Standard', 'HD']
NAME             = 'Treehouse'
ICON             = 'icon-default.png'
ART              = 'art-default.png'

def buildUrl( showName ):
  return TH_FEED_URL % ( showName, Prefs['feedToken'] )

##########################################################################################
def Start():
  Plugin.AddPrefixHandler(TH_PREFIX, MainMenu, NAME, ICON, ART)
  Plugin.AddViewGroup("Details", viewMode = "InfoList", mediaType = "items")
  ObjectContainer.title1 = NAME
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  HTTP.CacheTime = CACHE_INTERVAL

##########################################################################################
def MainMenu():
  dir = ObjectContainer(title1=NAME)
  for name in CATEGORIES:
    Log.Debug(name)
    dir.add(
      DirectoryObject(
        key=Callback(CategoryMenu, name=name, categories=CATEGORIES[name]),
        title=name))
  dir.add(PrefsObject(title=L("Preferences...")))
  return dir

##########################################################################################
def CategoryMenu(name, categories):
  dir = ObjectContainer(title1=NAME, title2=name)
  for category in categories:
    dir.add(
      DirectoryObject(
        key=Callback(GetFeed, path=category['path']),
        title=category['title'],
        thumb=R(category['icon'])))
  return dir

##########################################################################################
def GetFeed(path):
  try:
    request = HTTP.Request(buildUrl(path)) #, errors='ignore'
    feedContent = request.content
  except:
    return ObjectContainer(header=L("Error"), message=L("Check your feedToken!"))

  encoding = feedContent.split('encoding="')[1].split('"')[0]
  feedContent = feedContent.decode(encoding, 'ignore').encode('utf-8')
  feedObject = RSS.FeedFromString(feedContent)


  dir = ObjectContainer(title1=NAME, title2=feedObject.feed.subtitle)

  for episode in feedObject.entries:
    title = episode.title.replace('&#39;',"'").replace('&amp;','&')
    date = datetime.date.fromtimestamp(time.mktime(episode.updated_parsed))
    url = ""
    for link in episode.links:
      if re.search("^text", link.type):
        url = link.href
    if not url: continue
    summary = re.sub(r'<[^<>]+>', '', episode.summary)
    thumb = feedObject.feed.image.href

    dir.add(VideoClipObject(
      url = url,
      title = title,
      summary = summary,
      originally_available_at = date,
      thumb = thumb))

  return dir

