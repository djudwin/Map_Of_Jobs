import re

TARGET_OS = 'WIN' # WIN,MAC

file_text = ''
with open("templates/index.html") as f:
	content = f.readlines()
	for x in content:
		re_result = re.match(r"(.*)(filename='[\w\/]+.*')(.*)",x)
		if re_result:
			if TARGET_OS == 'WIN':
				file_text += re_result.group(1) + re_result.group(2).replace('/','\\\\') + re_result.group(3)
			else:	
				file_text += re_result.group(1) + re_result.group(2).replace('\\\\','/') + re_result.group(3)
		else:
			file_text += x

f_write = open("templates/index.html","w")
f_write.write(file_text)
f_write.close()