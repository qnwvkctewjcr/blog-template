class ArticleMetadataReverseYield{

    constructor(rootDataUrl){
        var self = this;
        self.rootDataUrl = rootDataUrl;

        self.yyyymm_to_data_dict = null;
        self.yyyymmListLen = null;

        self.article_data_list = null;
        self.articleDataListLen = null;
        
        self.done = false;
    }

    nextPromise(){
        var self = this;
        return Promise.resolve()
        .then(function(){
            return self._nextPromise_popArticleDataList();
        });
    }
    
    _nextPromise_popArticleDataList(){
        var self = this;
        if(self.article_data_list==null) return self._nextPromise_popYyyymmList();
        if(self.articleDataListLen<=0) return self._nextPromise_popYyyymmList();
        var ret = self.article_data_list[self.articleDataListLen-1];
        self.articleDataListLen -= 1;
        return ret;
    }
    
    _nextPromise_popYyyymmList(){
        var self = this;
        if(self.yyyymm_to_data_dict==null) return self._nextPromise_loadRootData();
        if(self.yyyymmListLen<=0) return Promise.reject("ArticleMetadataReverseYield.DONE");
        var yyyymmList = Object.keys(self.yyyymm_to_data_dict);
        yyyymmList = yyyymmList.sort();
        var yyyymm = yyyymmList[self.yyyymmListLen-1];
        var data_path = self.yyyymm_to_data_dict[yyyymm]["data_path"];
        self.yyyymmListLen-=1;
        return jsonPromise(URL_ROOT+"/"+data_path)
            .then(function(data){
                self.article_data_list = data["article_data_list"];
                self.articleDataListLen = self.article_data_list.length;
                return self._nextPromise_popArticleDataList();
            });
    }
    
    _nextPromise_loadRootData(){
        var self = this;
        return jsonPromise(self.rootDataUrl)
            .then(function(data){
                self.yyyymm_to_data_dict = data["yyyymm_to_data_dict"];
                self.yyyymmListLen = Object.keys(self.yyyymm_to_data_dict).length;
                return self._nextPromise_popYyyymmList();
            });
    }

    isDone(){
        var self = this;
        return self.done;
    }

};

var localJsonCache = {};
function jsonPromise(url){
    return Promise.resolve()
    .then(function(){
        if(url in localJsonCache)return localJsonCache[url];
        return $.getJSON(url)
        .then(function(data){
            localJsonCache[url]=data;
            return data;
        });
    });
}
