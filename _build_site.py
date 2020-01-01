import argparse
import datetime
import hashlib
import itertools
import jinja2
import jinja2.meta
import json
import os
import shutil

MY_PATH = os.getcwd()

def main(profile=None):
    if profile is None: profile = 'prod'
    
    conf_data = read_json(os.path.join(MY_PATH,'profiles',profile,'conf.json'))

    OUTPUT_PATH = conf_data['OUTPUT_PATH']
    OUTPUT_PATH = os.path.join(MY_PATH, OUTPUT_PATH)

    URL_ROOT = conf_data['URL_ROOT']

    template_loader = jinja2.FileSystemLoader(searchpath=['templates','blogs'])
    template_env = jinja2.Environment(loader=template_loader)
    blog_input_path = os.path.join(MY_PATH, 'blogs')
    docs_output_path = OUTPUT_PATH

    article_data_list = find_file(blog_input_path)
    article_data_list = filter(lambda i:i.endswith('.html.jinja'),article_data_list)
    article_data_list = [ {'input_abspath':i} for i in article_data_list ]
    for article_data in article_data_list:
        article_data['input_relpath'] = os.path.relpath(article_data['input_abspath'], blog_input_path)
        article_template = template_env.get_template(article_data['input_relpath'])
        article_data['yyyymmdd'] = article_template.module.date
        article_data['datetime'] = datetime.datetime.strptime(article_template.module.date,'%Y-%m-%d')
        order = article_template.module.order
        article_data['order'] = order
        article_data['title'] = article_template.module.title
        article_data['tag_list'] = article_template.module.tag_list
        yyyy = article_data['datetime'].strftime('%Y')
        mm = article_data['datetime'].strftime('%m')
        dd = article_data['datetime'].strftime('%d')
        article_data['yyyymm'] = article_data['datetime'].strftime('%Y-%m')
        filename = f'{article_template.module.filename}.html' if hasattr(article_template.module,'filename') else \
                                   os.path.basename(article_data['input_abspath'])[:-6]
        filename = f'{order:02d}-{filename}'
        article_data['filename'] = filename
        # output_basename = os.path.basename(article_data['input_abspath'])[:-6]
        article_data['output_html_relpath'] = os.path.join('articles',yyyy,mm,dd,article_data['filename'])
        article_data['output_html_abspath'] = os.path.join(docs_output_path,article_data['output_html_relpath'])

        article_id = sha256(article_data['output_html_relpath'])
        article_data['article_id'] = article_id
        article_data['output_data_relpath'] = os.path.join('datas','articles',article_id[:2],f'{article_id}.json')
        article_data['output_data_abspath'] = os.path.join(docs_output_path,article_data['output_data_relpath'])

        article_data['j'] = { k : article_data[k] for k in ['yyyymmdd','order','tag_list','output_html_relpath','output_data_relpath','title','filename','article_id'] }
        # print(article_data)

    # check same output_html_abspath
    output_abspath_to_article_data_list = to_list_dict(lambda i: i['output_html_abspath'], article_data_list)
    output_abspath_to_article_data_list = output_abspath_to_article_data_list.items()
    output_abspath_to_article_data_list = filter(lambda i:len(i[1])>1, output_abspath_to_article_data_list)
    output_abspath_to_article_data_list = list(output_abspath_to_article_data_list)
    if len(output_abspath_to_article_data_list) > 0:
        print('POFESCNO ERR: exist same output_abspath')
        print(output_abspath_to_article_data_list)
        exit(1)

    # build article
    for article_data in article_data_list:
        render_param = { 'URL_ROOT': URL_ROOT }

        output_html_abspath = article_data['output_html_abspath']
        output_html_abspath_dirname = os.path.dirname(output_html_abspath)
        makedirs(output_html_abspath_dirname)

        article_block_template = template_env.get_template(article_data['input_relpath'])
        article_block = article_block_template.render(**render_param)
        render_param['article_block'] = article_block

        article_template = template_env.get_template('article_page.html.jinja')
        article_template.stream(**render_param,**(article_block_template.module.__dict__)).dump(output_html_abspath)
        
        data = article_data['j']
        data = dict(data)
        data['content_html'] = article_block
        write_json(article_data['output_data_abspath'], data)

    # build index
    template_env.get_template('index.html.jinja') \
      .stream(URL_ROOT=URL_ROOT).dump(os.path.join(OUTPUT_PATH,'index.html'))

    # for yyyymm
    yyyymm_to_article_data_list_dict = to_list_dict(lambda i: i['yyyymm'], article_data_list)
    yyyymm_to_data_dict = {}
    for yyyymm, _article_data_list in yyyymm_to_article_data_list_dict.items():
        j_relpath = os.path.join('datas','yyyymms',f'{yyyymm}.json')
        j_path = os.path.join(docs_output_path,j_relpath)
        __article_data_list = _article_data_list
        __article_data_list = list(map(lambda i:i['j'], __article_data_list))
        __article_data_list.sort(key=lambda i:(i['yyyymmdd'],i['order']))
        data = {
            'yyyymm': yyyymm,
            'article_data_list': __article_data_list,
        }
        write_json(j_path, data)
        yyyymm_to_data_dict[yyyymm] = {
            'data_path': j_relpath
        }
    
    # for tag-yyyymm
    tag_to_article_data_list_dict = to_list_dict0(lambda i: i['tag_list'], article_data_list)
    tag_to_data_dict = {}
    for tag, _article_data_list in tag_to_article_data_list_dict.items():
        _yyyymm_to_article_data_list_dict = to_list_dict(lambda i: i['yyyymm'], _article_data_list)
        _yyyymm_to_data_dict = {}
        for yyyymm, __article_data_list in _yyyymm_to_article_data_list_dict.items():
            ___article_data_list = __article_data_list
            ___article_data_list = list(map(lambda i:i['j'], ___article_data_list))
            ___article_data_list.sort(key=lambda i:(i['yyyymmdd'],i['order']))

            j_relpath = os.path.join('datas','tags',tag,'yyyymm',yyyymm,f'{tag}-{yyyymm}.json')
            j_path = os.path.join(docs_output_path,j_relpath)
            data = {
                'tag': tag,
                'yyyymm': yyyymm,
                'article_data_list': ___article_data_list,
            }
            write_json(j_path, data)

            _yyyymm_to_data_dict[yyyymm] = {
                'tag': tag,
                'yyyymm': yyyymm,
                'data_path': j_relpath,
            }

        j_relpath = os.path.join('datas','tags',tag,f'{tag}.json')
        j_path = os.path.join(docs_output_path,j_relpath)
        data = {
            'tag': tag,
            'yyyymm_to_data_dict': _yyyymm_to_data_dict,
        }
        write_json(j_path, data)

        tag_to_data_dict[tag] = {
            'tag': tag,
            'data_path': j_relpath
        }

    # output root data
    write_json(
        os.path.join(docs_output_path,'datas','data.json'),
        {
            'yyyymm_to_data_dict': yyyymm_to_data_dict,
            'tag_to_data_dict': tag_to_data_dict,
        }
    )

    copy_tree(os.path.join(MY_PATH,'static'), OUTPUT_PATH)

def to_list_dict(k_lambda, data_list):
    ret_dict = {}
    for data in data_list:
        k = k_lambda(data)
        if k not in ret_dict:
            ret_dict[k] = []
        ret_dict[k].append(data)
    return ret_dict

def to_list_dict0(kl_lambda, data_list):
    ret_dict = {}
    for data in data_list:
        kl = kl_lambda(data)
        for k in kl:
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

def write_json(path, data):
    makedirs(os.path.dirname(path))
    with open(path, mode='wt') as fout:
        fout.write(json.dumps(data, sort_keys=True, indent=2))
        fout.write('\n')

def read_json(path):
    with open(path, mode='r') as fin:
        return json.load(fin)

def copy_tree(src, dst):
    for root, _, files in os.walk(src):
        for file in files:
            src_abspath = os.path.join(root, file)
            relpath = os.path.relpath(src_abspath, src)
            tar_abspath = os.path.join(dst, relpath)
            makedirs(os.path.dirname(tar_abspath))
            shutil.copy(src_abspath, tar_abspath)

def sha256(s):
    m = hashlib.sha256()
    m.update(s.encode('utf8'))
    return m.hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('profile', nargs='?')
args = parser.parse_args()

main(**(args.__dict__))
