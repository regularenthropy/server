import sys
import os
import msg
import tldextract
import yaml


def is_in_untrusted_domain(root_domain, domain):
    if root_domain in untrusted_domains:
        return True
    elif domain in untrusted_domains:
        return True
    else:
        return False


def is_in_blockwords(title, listname):
    for block_word in blockwords:
        if block_word in title:
            return True
    return False
            

def chk_title(title, content, root_domain, domain):
    if is_in_blockwords(title, "detect_words"):
        if is_in_untrusted_domain(root_domain, domain):
            return True

    if content != "NO_DATA":
        if is_in_blockwords(content, "detect_words"):
            if is_in_untrusted_domain(root_domain, domain):
                return True
        
        if is_in_blockwords(content, "block_words"):
            return True

    if is_in_blockwords(title, "block_words"):
        return True

    return False


def chk_domain(root_domain, domain):
    pass


def chk_result(search_result):
    url = search_result["url"]
    domain = search_result["parsed_url"][1]
    title = search_result["title"]
    
    try:
        content = search_result["content"]
    except KeyError as e:
        content = "NO_DATA"
    extracted = tldextract.extract(url)

    root_domain = "{}.{}".format(extracted.domain, extracted.suffix)
    
    if blocklist.chk_domain(root_domain, domain):
        return False
    elif blockwords.chk_title(title, content, root_domain, domain):
        return False
    else:
        return True
