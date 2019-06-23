#!/usr/bin/bash


#query=('兇') 
query=('眼鏡' '長腿' '蘿莉' 'OL' '姊姊' '子瑜' '兇') 

for i in ${query[*]} ;do
	echo $i | python3 retrieval_example.py -i inverted_file_1500_title.json > result/${i}_title.html &
	echo $i | python3 retrieval_example.py -i inverted_file_1500_content.json > result/${i}_content.html &
	echo $i | python3 retrieval_example.py -i inverted_file_1500_upvote.json > result/${i}_upvote.html &
	echo $i | python3 retrieval_psedo.py -i inverted_file_1500_title.json > result/${i}_psedo_title.html &
	echo $i | python3 retrieval_psedo.py -i inverted_file_1500_content.json > result/${i}_psedo_content.html &
	echo $i | python3 retrieval_psedo.py -i inverted_file_1500_upvote.json > result/${i}_psedo_upvote.html &
	echo $i | python3 retrieval_title_content.py > result/${i}_title_content.html &
	echo $i | python3 retrieval_title_content_push.py > result/${i}_title_content_push.html &
	echo $i | python3 retrieval_title_content_push_pushcnt.py > result/${i}_title_content_push_pushcnt.html 
	#echo ${i}_abc
done
