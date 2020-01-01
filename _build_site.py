import datetime
import jinja2
import jinja2.meta
import os
import shutil

MY_PATH = os.getcwd()

def main():

    template_loader = jinja2.FileSystemLoader(searchpath=['templates','blogs'])
    template_env = jinja2.Environment(loader=template_loader)
    blog_input_path = os.path.join(MY_PATH, 'blogs')
    docs_output_path = os.path.join(MY_PATH, 'docs')

    article_data_list = find_file(blog_input_path)
    article_data_list = filter(lambda i:i.endswith('.html.jinja'),article_data_list)
    article_data_list = [ {'input_abspath':i} for i in article_data_list ]
    for article_data in article_data_list:
        article_data['input_relpath'] = os.path.relpath(article_data['input_abspath'], blog_input_path)
        article_template = template_env.get_template(article_data['input_relpath'])
        article_data['datetime'] = datetime.datetime.strptime(article_template.module.date,'%Y-%m-%d')
        article_data['order'] = article_template.module.order
        article_data['tag_list'] = article_template.module.tag_list
        yyyy = article_data['datetime'].strftime('%Y')
        mm = article_data['datetime'].strftime('%m')
        article_data['yyyymm'] = article_data['datetime'].strftime('%Y-%m')
        output_basename = os.path.basename(article_data['input_abspath'])[:-6]
        article_data['output_abspath'] = os.path.join(docs_output_path,'blogs',yyyy,mm,output_basename)
        # print(article_data)

    # check same output_abspath
    output_abspath_to_article_data_list = to_list_dict(article_data_list, lambda i: i['output_abspath'])
    output_abspath_to_article_data_list = output_abspath_to_article_data_list.items()
    output_abspath_to_article_data_list = filter(lambda i:len(i[1])>1, output_abspath_to_article_data_list)
    output_abspath_to_article_data_list = list(output_abspath_to_article_data_list)
    if len(output_abspath_to_article_data_list) > 0:
        print('POFESCNO ERR: exist same output_abspath')
        print(output_abspath_to_article_data_list)
        exit(1)

    # build article
    for article_data in article_data_list:
        article_template = template_env.get_template(article_data['input_relpath'])
        output_abspath = article_data['output_abspath']
        output_abspath_dirname = os.path.dirname(output_abspath)
        makedirs(output_abspath_dirname)
        article_template.stream().dump(output_abspath)

def to_list_dict(data_list, k_lambda):
    ret_dict = {}
    for data in data_list:
        k = k_lambda(data)
        if k not in ret_dict:
            ret_dict[k] = []
        ret_dict[k].append(data)
    return ret_dict

def find_file(dir):
    file_list = []
    for root, _, files in os.walk(dir):
        for file in files:
            yield os.path.join(root, file)

def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

main()
