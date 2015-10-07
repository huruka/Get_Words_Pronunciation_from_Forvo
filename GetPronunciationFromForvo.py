#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re
import requests
import logging
from bs4 import BeautifulSoup
import getpass

wrk_dir = os.getcwd()
logging.basicConfig(filename = os.path.join(wrk_dir, 'LOG.txt'), level = logging.DEBUG, format = '%(asctime)s - %(levelname)s: %(message)s')
log = logging.getLogger('root')

def main():
	def signin(username, password):
		signin_url = 'http://forvo.com/login'
		logininfo = {'login': username, 'password': password}
		user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
					  'AppleWebKit/537.36 (KHTML, like Gecko) '
					  'Chrome/45.0.2454.101 Safari/537.36'
					  )
		post_headers = {'User-Agent': user_agent,
						'Referer': 'http://forvo.com/login'
						}
		login_res = forvo_session.post(signin_url,
									 data=logininfo,
									 headers=post_headers,
									 )
		if login_res.status_code == 200:
			print('Login Successfully!')
		else:
			log.error('Login failed...')
			sys.exit(2)

	def save_pron_media(media_url, save_path):
		media_response = forvo_session.get(media_url, stream=True)
		with open(save_path, 'wb') as fd:
			for chunk in media_response.iter_content(chunk_size=1024):
				if chunk:	 # filter out keep-alive new chunks
					fd.write(chunk)
	
	def get_pron_media_links(word, lang = 'ja'):				#lang值：en, ja
		locale_dict = {'ja' : 'Japan', 'en' : 'United'}
		word_url = r'http://forvo.com/word/%s/#%s' % (word, lang)
		word_url_response = forvo_session.get(word_url)
		word_response_text = word_url_response.text
		soup = BeautifulSoup(word_response_text, 'html.parser')
		pron_groups = soup.article.ul('li')
		media_links = dict()
		for i in pron_groups:
			if locale_dict[lang] in i.select('.from')[0].string:
				if i.select('.uLink'):
					pronunciationer = i.select('.uLink')[0].string
				else:
					break
				link = i.select('.download > a')[0].attrs.get('href')
				media_links.update({pronunciationer : link})
		return media_links

	forvo_session = requests.session()

	username = input('请输入FORVO用户名: ')
	password = getpass.getpass('输入密码: ')
	signin(username, password)

	with open(os.path.join(wrk_dir, 'words.txt'), encoding = 'utf-8') as wf:
		wf_content = wf.read()
		matches = re.search('^#language:\s*?(\S+?)\n', wf_content, re.M)
		if matches:
			lang = matches.group(1)
		words = re.findall('^([^#]+?)\s?$', wf_content, re.M)
	
	save_dir = os.path.join(wrk_dir, 'words_pronunciation')
	if not os.path.exists(save_dir):
		os.makedirs(save_dir)
	for word in words:
		media_dict = get_pron_media_links(word, lang)
		for pronunciationer, link in media_dict.items():
			save_path = os.path.join(save_dir, '%s_by_%s.mp3' % (word, pronunciationer))
			save_pron_media(link, save_path)

try:
	main()
except Exception as e:
	log.exception('e')