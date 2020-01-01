function getLatestArticleMetadataPromise(){
    return $.getJSON(URL_ROOT+"/datas/data.json")
        .then(function(data){
            //console.log(data);
            
            var yyyymm_to_data_dict = data["yyyymm_to_data_dict"];
            //console.log(Object.keys(yyyymm_to_data_dict));
    
            var max_yyyymm = Object.keys(yyyymm_to_data_dict);
            max_yyyymm = max_yyyymm.sort();
            max_yyyymm = max_yyyymm[max_yyyymm.length-1];
            //console.log(max_yyyymm);
    
            return $.getJSON(URL_ROOT+"/"+yyyymm_to_data_dict[max_yyyymm]["data_path"]);
        })
        .then(function(data){
            //console.log(data);
            
            var article_data_list = data["article_data_list"];
            
            var ret = article_data_list[article_data_list.length-1];
            
            return ret;
        });
}

function getPreviousArticleMetadataPromise(sortKey){
    var yyyymm = sortKey.substring(0,7);
    var dataPath = null;
    var dataPath1 = null;
    return $.getJSON(URL_ROOT+"/datas/data.json")
        .then(function(data){
            var yyyymm_to_data_dict = data["yyyymm_to_data_dict"];
            
            dataPath = yyyymm_to_data_dict[yyyymm]["data_path"];
            
            var yyyymmList = Object.keys(yyyymm_to_data_dict);
            var yyyymm1=null;
            for(var ki in yyyymmList){
                var k = yyyymmList[ki];
                if(k>=yyyymm)continue;
                if((yyyymm1!=null)&&(k<yyyymm1))continue;
                yyyymm1 = k;
            }
            dataPath1 = yyyymm_to_data_dict[yyyymm1]["data_path"];
            
            return $.getJSON(URL_ROOT+"/"+dataPath);
        })
        .then(function(data){
            var article_data_list = data["article_data_list"];
            
            var best_article_data = null;
            for(var i in article_data_list){
                var article_data = article_data_list[i];
                if(article_data["sort_key"]>=sortKey)continue;
                if((best_article_data!=null)&&(article_data["sort_key"]<best_article_data["sort_key"]))continue;
                best_article_data = article_data;
            }
            
            if(best_article_data!=null)return best_article_data;
            
            return $.getJSON(URL_ROOT+"/"+dataPath1)
                .then(function(data){
                    var article_data_list = data["article_data_list"];
                    var ret = article_data_list[article_data_list.length-1];
                    return ret;
                });
        });
}
