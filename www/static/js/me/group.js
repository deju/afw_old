$(document).ready(function(){



$Group = jQuery.afewords.user_group || {};



$Group.group_create = function(obj){
    /** create group ajax **/
    var mes = $("#group_create_table").DivToDict();
    var $button = $(obj);
    var process = $("span.g_c_process");
    if(mes['group_name']==''){
        process.html('请您填写小组名！').css('color','red');
        return false;
    }
    /*
    if(mes['group_class']==''){
        process.html('请您填写小组分类！').css('color','red');
        return false;
    }*/
    if(mes['group_des']==''){
        process.html('请您简单描述一下小组！').css('color','red');
        return false;
    }
    /*********** data ok, send it ******************/
    $.postJSON('/group-create', mes, 
    function(){
        process.html('<img src="/static/img/ajax.gif" />');
        $button.attr("disabled",'disabled').css('color','#ccc');
    },
    function(response){
        if(response.kind==0){
            setTimeout('location.href="/group-set-logo?id='+ response.info +'"', 1000);
        }else{
            process.html(response.info).css('color', "red");
            $button.removeAttr("disabled").css("color", "black");
        }
    },
    function(response){
            process.html('提交数据出错！').css('color', "red");
            $button.removeAttr("disabled").css("color", "black");
    });
}



group_logo_handler = function(){
    
}





});