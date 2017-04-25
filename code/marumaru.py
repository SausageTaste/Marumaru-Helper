import re
import urllib.parse


IMAGE_DOMAIN_T = ('http://www.shencomics.com/', 'http://www.yuncomics.com/', 'http://blog.yuncomics.com/',
                  "http://shencomics.com/", "http://1.bp.blogspot.com/", "http://2.bp.blogspot.com/",
                  "http://3.bp.blogspot.com/", "http://4.bp.blogspot.com/", "http://5.bp.blogspot.com/",
                  "http://i.imgur.com/")
CHAPTER_DOMAIN_T = ("http://www.shencomics.com/", 'http://www.yuncomics.com/', 'http://blog.yuncomics.com/',
                    "http://shencomics.com/", "http://wasabisyrup.com/")
IMAGE_EXTENSION_T = ('.jpg', '.JPG', '.png', '.PNG', '.gif', '.GIF', '.bmp', '.BMP', '.jpeg', '.JPEG')
FAILED_HTML_S = "<html><head></head><body></body></html>"
JAVASCRIPT_REQUIRED_S = "Javascript is required. Please enable javascript before you are allowed to see this page."
BLACK_LIST = ("http://marumaru.in/like.png", "http://marumaru.in/layouts/tiny01/image/share_f.png")


class MarumaruError(Exception):
    def __str__(self):
        return "General error."

class WTF(MarumaruError):
    def __str__(self):
        return "This exception is not what I expected to happen. Debug youself, sorry."

class FailedToFindChapterName(MarumaruError):
    def __str__(self):
        return "Failed to find this chapter's name."

class FailedToFindAnyImage(MarumaruError):
    def __str__(self):
        return "No image link was found. Chances are that given html source is not valid."

class FailedToFindThumbnail(MarumaruError):
    def __str__(self):
        return "Yeah"

class OddlyShortHTML(MarumaruError):
    def __init__(self, length):
        self.length = length

    def __str__(self):
        return "The length of given HTML source is {}, which is too small for a marumaru source.".format(self.length)

class BiggerBlogspotFound(MarumaruError):
    def __str__(self):
        return "5.bp.blogspot.com/ found."

class JavascriptError(MarumaruError):
    def __str__(self):
        return "You need to get html with a  web browser that supports Javascript."


class ProtectedChapter(MarumaruError):
    def __str__(self):
        return "shit"


def remove_resize(origin_url:str):
    a_url = origin_url
    for x_s in IMAGE_EXTENSION_T:
        if a_url.endswith(x_s):
            a_url = a_url[:-len(x_s)]
            try:
                cut_i = a_url.rindex('-')
            except ValueError:
                return origin_url
            else:
                size_s = a_url[cut_i + 1:]
                a_url = a_url[:cut_i]
                if size_s.count('x'):
                    for y_s in size_s.split('x'):
                        try:
                            int(y_s)
                        except ValueError:
                            return origin_url
                        else:
                            pass
                    new_url_s = a_url + x_s
                    print("Resize {} -> {}".format(origin_url, new_url_s))
                    return new_url_s
                else:
                    return origin_url
        else:
            return origin_url

def img_class_gen(html_s:str):
    st_point_i = 0
    while True:
        try:
            head_i = html_s.index("<img", st_point_i)
            tail_i = html_s.index(">", head_i) + 1
        except ValueError:
            break
        else:
            st_point_i = tail_i
            yield html_s[head_i:tail_i]

def divide_tags(string:str):
    cut_l = []
    start_point_i = 0
    while True:
        index_l = []
        try:
            index_l.append(string.index("<", start_point_i))
        except ValueError:
            pass
        try:
            index_l.append(string.index(">", start_point_i))
        except ValueError:
            pass
        if not index_l:
            break
        index_l.sort()
        cut_l.append(index_l[0])
        start_point_i = index_l[0] + 1

    divided_l = []
    for x, head_i in enumerate(cut_l):
        try:
            tail_i = cut_l[x+1] + 1
        except:
            divided_one_s = string[head_i:]
        else:
            divided_one_s = string[head_i:tail_i]
        divided_one_s = divided_one_s.lstrip(">")
        divided_one_s = divided_one_s.rstrip("<")
        # Exclude shits

        if not divided_one_s:
            continue
        elif divided_one_s == '\n':
            continue
        elif divided_one_s == ' ':
            continue

        divided_l.append(divided_one_s)

    return divided_l

def url_encode(url):
    divided = re.findall('[^ ]', url)
    for x, x_s in enumerate(divided):
        if not is_unicode(x_s):
            encoded_one = urllib.parse.quote(x_s)
            divided[x] = encoded_one
    return ''.join(divided)

def is_unicode(x):
    fine_char_t = ('/', '\ufeff', ".", "_", "-", "\\", "%", "?", "=", "&")
    a = len(re.findall('[:A-Za-z0-9]', x))
    for x_s in fine_char_t:
        a += x.count(x_s)

    if a == 0:
        return False
    elif a > 0:
        return True
    else:
        raise WTF

def is_manga_url(url:str):
    if url.count("marumaru.in/"):
        return True
    else:
        return False

def is_m_chapter_url(url:str):
    for x in CHAPTER_DOMAIN_T:
        if url.count(x):
            return True
    return False

def is_m_image_url(url:str):
    for x in IMAGE_DOMAIN_T:
        if url.count(x):
            return True
    return False

def is_image(x:str):
    for y in IMAGE_EXTENSION_T:
        if x.count(y):
            return True
    return False

def is_valid_chap_html(html_s:str):
    if html_s.count("Protected"):
        raise ProtectedChapter
    if len(html_s) < 10000:
        return False
    else:
        return True

def get_extension_from_url(a_url_s:str):
    for x_s in IMAGE_EXTENSION_T:
        if a_url_s.count(x_s):
            return x_s
    raise WTF


class MarumaruManga:
    """
    This class deals with source code of marumaru chapters page so don't insert url.
    Chapters page is the page that include all chapters' link.
    Don't be confused with chapter page where you actually read a manga.
    MarumaruChapter class will deal with it.
    """
    def __init__(self, top_source:str):
        if top_source.count("Protected"):
            raise ProtectedChapter
        if len(top_source) < 10000:
            raise OddlyShortHTML(len(top_source))
        else:
            self.__source = top_source

    def chapters_gen(self):
        html_s = self.__source
        c = 0
        while True:
            try:
                # get string between <a> and </a>
                head_to_cut = html_s.index('<a')
                tail_to_cut = html_s.index('</a')
                a_tag = html_s[head_to_cut:tail_to_cut]
                html_s = html_s[tail_to_cut + 3:]
            except ValueError:
                break
            else:
                # get href=" " as url
                try:
                    # print(repr(a_tag))
                    head_to_cut = a_tag.index('href="')
                    url = a_tag[head_to_cut + 6:]
                    tail_to_cut = url.index('"')
                    url = url[:tail_to_cut]
                    if not is_m_chapter_url(url):
                        continue
                except ValueError:
                    pass
                else:
                    # get name of the chapter
                    for x_s in divide_tags(a_tag):
                        if not x_s.startswith('<'):
                            name = x_s
                            break
                    else:
                        continue

                    # fix shits
                    name = name.strip(' ')
                    name = name.strip("&nbsp;")
                    if name == "\ufeff":
                        continue
                    if not name:
                        continue

                    if name.count("&nbsp;"):
                        name = ' '.join(name.split("&nbsp;"))

                    yield (name, url)
                    c += 1

    def chapters(self)->list:
        return list(self.chapters_gen())

    def chapter_urls(self):
        a_list = []
        for x_name_s, x_url_s in self.chapters_gen():
            if x_url_s in a_list:
                continue
            a_list.append(x_url_s)
        return a_list

    def chapter_names(self):
        a_list = []
        for x_name_s, x_url_s in self.chapters_gen():
            if x_name_s in a_list:
                continue
            a_list.append(x_name_s)
        return a_list

    def manga_title(self):
        """
        Returns title of the manga, not of a chapter.
        You don't need to call self.fetch_chapters() for this.
        """
        try:
            head_cut_i = self.__source.index('<title>') + 7
            tail_cut_i = self.__source.index('</title', head_cut_i)
        except ValueError:
            return None
        else:
            title_s = self.__source[head_cut_i:tail_cut_i]
            if title_s.startswith("MARUMARU - 마루마루 -"):
                title_s = title_s[17:]
            title_s = title_s.strip()
            return title_s

    def thumbnail_link_dummy(self):
        html_s = self.__source
        head_cut = html_s.index('<img src="http://marumaru.in/quickimage/') + 10
        tail_cut = html_s.index('"',  head_cut)
        return html_s[head_cut:tail_cut]

    def thumbnail_link(self):
        html_s = self.__source
        last_tail = 0
        while True:
            try:
                head_cut = html_s.index("<div", last_tail)
                tail_cut = html_s.index("</div", head_cut)
            except ValueError:
                raise FailedToFindThumbnail
            else:
                a_tag_s = html_s[head_cut:tail_cut]
                last_tail = tail_cut
                if a_tag_s.count("src"):
                    head_cut = a_tag_s.index("src=") + 5
                    tail_cut = a_tag_s.index('"', head_cut)
                    a_url_s = a_tag_s[head_cut:tail_cut]
                    if is_image(a_url_s) and a_url_s.count("http://"):
                        if a_url_s not in BLACK_LIST:
                            return a_url_s


class MarumaruChapter:
    """
    This class deals with source code of marumaru chapter page so don't insert url.
    Chapter page is the page where you actually read a manga.
    Don't be confused with chapters page that include all chapters' link.
    MarumaruManga class will deal with it.
    """
    def __init__(self, chapter_source:str):
        if JAVASCRIPT_REQUIRED_S in chapter_source:
            raise JavascriptError
        if chapter_source.count("Protected"):
            raise ProtectedChapter
        elif len(chapter_source) < 10000:
            raise OddlyShortHTML(len(chapter_source))
        else:
            self.__source = chapter_source

    def image_links_gen_dum(self):
        html_s = self.__source

        for x_s in img_class_gen(html_s):
            for y_s in IMAGE_DOMAIN_T:
                try:
                    head_i = x_s.index(y_s)
                    tail_i = x_s.index('"',  head_i)
                except ValueError:
                    pass
                else:
                    a_url = x_s[head_i:tail_i]
                    # exclude
                    if a_url.count("우마루세로"):
                        continue
                    a_url = remove_resize(a_url)
                    a_url = url_encode(a_url)
                    yield a_url

    def image_links(self, resized:bool=True) -> iter:
        html_s = self.__source

        last_tail_i = 0
        while True:
            try:
                head_cut = html_s.index("<img class", last_tail_i)
                tail_cut = html_s.index(">", head_cut)
            except ValueError:
                break
            else:
                last_tail_i = tail_cut
                a_url_s = html_s[head_cut:tail_cut]
                try:
                    head_s_cut = a_url_s.index('data-src="') + 10
                    tail_s_cut = a_url_s.index('"', head_s_cut)
                except ValueError:
                    print("fucker")
                    continue
                else:
                    a_url_s = "http://wasabisyrup.com" + a_url_s[head_s_cut:tail_s_cut]
                    if not resized:
                        a_url_s = remove_resize(a_url_s)
                    a_url_s = url_encode(a_url_s)
                    yield a_url_s

    def chapter_name(self):
        source = self.__source
        try:
            head_to_cut = source.index('<title>') + 7
            tail_to_cut = source.index('</title')
        except ValueError:
            raise FailedToFindChapterName
        else:
            title_str = source[head_to_cut:tail_to_cut]

            if title_str.count('|'):
                title_str = title_str.split('|')[0]

            title_str = title_str.strip()
            return title_str


def main():
    import ezurl

    html_s = ezurl.url_urllib_html("http://www.yuncomics.com/archives/1686393")
    manga = MarumaruChapter(html_s)
    image_l = list(manga.image_links_syrup_gen())
    for x_s in image_l:
        print(x_s)
    print(len(image_l))


if __name__ == '__main__':
    main()
