$().ready(function(){


var feed_is_all = false;
var current_feed_id = 0;

get_feed_by_id = function(){
    var mes = {};
    mes['id'] = current_feed_id;

    if(feed_is_all!='yes'){
    $.postJSON('/feed',mes,
		function(){ 
            _process = '<div id="feed" class="feed_process">'+
                            '<div class="f-body">'+
                            '<div class="f-con"><img src="/static/img/loading_bar.gif" /></div></div></div>';
            $("#body_content").append(_process);
        },
		function(response){
			if(response.kind == 0){
                _html = '';
                result = response.info.feed;
                var ii = 0;
                
                for(ii in result){
                    //alert(tmp);
                    tmp = result[ii];
                    one_feed = '<div id="feed">'+
                            '<div class="f-body">'+
                            //'<div class="f-style"><img src="/static/img/button/pencil_ok1.png" /></div>'+
                            '<div class="f-control">'+
                            '<div class="f-author"><a href="/bloger/'+ tmp.author_id +'" target="_blank">'+ tmp.author_name +'</a>'+
                            '<span class="f-sub">-</span><span class="f-type">执笔</span></div>'+
                            //'<div class="f-comment"><span>0</span>评论</div>'+
                            '</div>'+
                            '<div class="f-con"><a href="/blog/'+ tmp.blog_id +'" target="_blank">'+ tmp.title +'</a></div>';
                    if(tmp.summary != '') { one_feed +='<div class="f-con">'+ tmp.summary + '</div>';}
                            one_feed += '<div>'+ tmp.view_body +'</div>';
                            one_feed +='</div>'+
                            '<div class="f-pic"><a href="/bloger/'+tmp.author_id+'" target="_blank"><img src="'+tmp.author_avatar+'" /></a></div>'+
                            '</div>';
                    _html += one_feed;
                }
                current_feed_id = response.info.last_id;
                feed_is_all = response.info.is_all;
                if(feed_is_all == 'yes'){  
                    _html += '<div id="feed">'+
                            '<div class="f-body">'+
                            '<div class="f-con">无更多动态</div></div></div>';
                }
                $("#body_content").children(".feed_process").remove();
                $("#body_content").append(_html);
                
            }else{

            }
            IS_LOADING = false;
		},
		function(response){

		}
	);
    }else{

    }	
}

var IS_LOADING = true;

$(window).scroll(function() {  
    var o = $('#middle');  
          
        // 并不是所有页面都要执行加载操作。  
        // 你也可以选择别的识别条件。  
    if(o!=null && o.length !=0){  
            
          //获取网页的完整高度(fix)  
      //var hght= window.scrollHeight;
        var hght = document.body.scrollHeight;
       //alert(hght);
      //获取浏览器高度(fix)  
      //var clientHeight =window.clientHeight;  
    var clientHeight = window.screen.height;
    //var scroll_top = document.body.scrollTop;
    //alert(scroll_top);
    //alert(clientHeight);
          //获取网页滚过的高度(dynamic)  
      var top= window.pageYOffset ||   
                        (document.compatMode == 'CSS1Compat' ?    
                        document.documentElement.scrollTop :   
                        document.body.scrollTop);  
        
  
          //当 top+clientHeight = scrollHeight的时候就说明到底儿了  
      if(top>=(parseInt(hght)-clientHeight)){  
        if(IS_LOADING==false)
        {
         IS_LOADING = true;
         get_feed_by_id();
        }
      }  
    }  
});
	





});