import re, string, urllib2, datetime, time

TH_PREFIX        = '/video/treehouse'
TH_FEED_URL      = 'http://teamtreehouse.com/library/%s.rss?feed_token=%s'
CACHE_INTERVAL   = 1800
FORMATS          = ['Standard', 'HD']
NAME             = 'Treehouse'
ICON             = 'icon-default.png'
ART              = 'art-default.png'

CATEGORIES = {
  'the-treehouse-show': {
    'title': 'The Treehouse Show',
    'icon': R('Treehouse_Show.png')
  },
  'treehouse-quick-tips': {
    'title': 'Treehouse Quick Tips',
    'icon': R('badges_QuickTips.png')
  },
  'treehouse-workshops': {
    'title': 'Treehouse Workshops',
    'icon': R('badges_workshops.png')
  },
  'design-and-development': {
    'title': 'Design and Development',
    'icon': R('badges_bonus_devdesign.png')
  },
  'exercise-your-creative': {
    'title': 'Exercise Your Creative',
    'icon': R('EYC.png')
  }
}

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
  for index in CATEGORIES:
    dir.add(
      DirectoryObject(
        key=Callback(GetFeed, name=index),
        title=CATEGORIES[index]['title'],
        thumb=CATEGORIES[index]['icon']))
  dir.add(PrefsObject(title=L("Preferences...")))
  return dir

##########################################################################################
def GetFeed(name):
  try:
    request = HTTP.Request(buildUrl(name)) #, errors='ignore'
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

