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
