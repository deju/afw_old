$().ready(function(){

jQuery.com_afewords_www_user = $.com_afewords_www_user || {};

$Login = jQuery.com.afewords.www.user_login || {};
$Set = jQuery.com.afewords.www.user_settings || {};

$AFW_User = $.com_afewords_www_user;
/******** bind function ********************/


$Login.repeat_time = 30;
$Login.repeat_tag = "#repeat_time";
$Login.repeat_tag_all = "#repeat_time_all";
$Login.repeat_email  = '';


$Login.set_repeat = function(tag, tag_all, email){
    $Login.repeat_time = 30;
    $Login.repeat_tag = tag;
    $Login.repeat_tag_all = tag_all;
    $Login.repeat_email  = email;
}


$Login.do_reg = function(obj){
    var target = $("#login");
	var mes = target.DivToDict();	
	var reg_process = target.find(".login-process"), reg_button = target.find("button");
	var email_reg = (/^\w+((-\w+)|(\.\w+))*@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/);
    function wrong(str){
        reg_process.html(str).css('color','red');  return false;
    };
    if(mes['name'] == ''){ wrong('请您填写姓名！'); return false;  }	
	if(mes['name'].length < 2){ wrong('姓名至少为两个字！'); return false;  }
	if(mes['email'] == '' || !email_reg.test(mes['email'])){ wrong('请您填写正确的邮箱！'); return false; }
	if(mes['pwd']=='' || mes['pwd'].length < 4){ wrong('请您设置登陆密码，至少为四位！'); return false;	}	
	if(mes['pwd'] != mes['pwd_again']){ wrong('确认密码错误！'); return false;	}
	if(mes['token'] == ''){ wrong('请填写验证码！'); return false; }
	$.postJSON("/reg", mes,
		function(){
			reg_process.html('<img src="/static/img/ajax.gif" />');
			reg_button.attr("disabled","disabled").css("color","#ccc");
		},
		function(response, status){
            reg_process.html('');
		    if(response.kind == 0){    
                 reg_process.html('验证邮件已经发送至您的邮箱！<span id="repeat_time_all"><span id="repeat_time" class="font-14">30</span>秒后可重新发送验证邮件！</span>').css('color','blue');
                 $Login.set_repeat("#repeat_time", "#repeat_time_all", mes['email']);
                 $Login.s30s_repeat();

		    }else{
		         wrong(response.info);
		         reg_button.removeAttr("disabled").css("color","#555");	
		         $Tool.change_code();
		    }
		},
		function(response){
			wrong("操作失败!");
			reg_button.removeAttr("disabled").css("color","#555");	
			$Tool.change_code();
			
		}	
	);
};



$Login.do_reset_password = function(obj){
    $Login.repeat_time = 30;
	var mes = $("#login").DivToDict();
	var reg_process = $(".login-process");
	var email_reg = (/^\w+((-\w+)|(\.\w+))*@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/);
	//alert('in reset');
	function wrong(str){
	   reg_process.html(str).css('color', 'red');  return false;
	}
	if(mes['email'] == '' || !email_reg.test(mes['email'])){	
		wrong('请您填写正确的邮箱！');
		return false;
	}
    if(mes['pwd'] == '' || mes['pwd'].length < 4){
	   wrong('请您设置新密码，4位以上！');
	   return false;    
	}	
	if(mes['pwd_again'] != mes['pwd']){
		wrong('您的确认密码填写有误，请核查！');
	   	return false;
	}
	if(mes['token'] == ''){
		wrong('请您填写验证码！');
	   	return false;
	}
	
	$.postJSON("/reset", mes,
		function(){
			reg_process.html('<img src="/static/img/ajax.gif" />');
			$(obj).attr("disabled","disabled").css("color","#ccc");
		},
		function(response){
		    if(response.kind == 0){
		         reg_process.html('密码重置邮件已经发送至您的邮箱！<span id="repeat_time_all"><span id="repeat_time" class="font-14">30</span>秒后可重新发送密码重置邮件！</span>').css('color','blue');
                 $Login.set_repeat("#repeat_time", "#repeat_time_all", mes['email']);
                 $Login.s30s_repeat();
		    }else{
		         wrong(response.info);
		         $(obj).removeAttr("disabled").css("color","#555");	
		    }
		},
		function(response){
			wrong('操作失败!');
			$(obj).removeAttr("disabled").css("color","#555");	
		}	
	); 
}



$Login.s30s_repeat = s30s_repeat =  function(){
    if($Login.repeat_time>0){
        $($Login.repeat_tag).html($Login.repeat_time--);
        setTimeout(s30s_repeat,1000);
    }else{
        //alert($(tag_all).html());
        var $tmp_link = $('<a></a>');
        $tmp_link.attr({"href":"javascript:void(0);", "email": $Login.repeat_email});
        $tmp_link.text('重新发送邮件');
        $($Login.repeat_tag_all).html('').append($tmp_link);
        $tmp_link.bind('click', function(){
              $Login.send_repeat_mail(this);
        });
        $Login.repeat_time = 30;
        //$(tag_all).html('<a href="javascript:void(0);"  email="'+email+'">重新发送邮件</a>');
        //$Login.repeat_time(true);
    }
}	


$Login.send_repeat_mail = function(obj){
    $Login.repeat_time = 30;
    var mes = {}
    mes['email'] = $.trim($(obj).attr("email"));	
	var reg_process = $(".login-process");
    //reg_info.html('');
    $.postJSON("/repeat-mail", mes,
		function(){
			reg_process.html('<img src="/static/img/ajax.gif" />');
		},
		function(response){
		    if(response.kind == 0){
		         reg_process.html('密码重置邮件已经发送至您的邮箱！<span id="repeat_time_all"><span id="repeat_time" class="font-14">30</span>秒后可重新发送邮件！</span>').css('color','blue');
                 $Login.set_repeat("#repeat_time", "#repeat_time_all", mes['email']);        
                 $Login.s30s_repeat();
		    }else{
		         reg_process.html(response.info);
		    }
		},
		function(response){
			reg_process.html('操作失败!').css('color','red');
		}	
	); 
}



$Login.do_login_check = do_login_check = function(){
	var mes = $("#login_do").DivToDict();
	var reg_info = $("span.login-process");	
	var email_reg = (/^\w+((-\w+)|(\.\w+))*@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/);

	if(mes['email'] == '' || !email_reg.test(mes['email'])){	
		reg_info.html('请您填写正确的邮箱！');
		return false;
	}

    if(mes['pwd'] == ''){
	   reg_info.html('请填写密码！');
	   return false;    
	}	
	
	if(mes.hasOwnProperty('token')){
	if(mes['token'] == ''){
		reg_info.html('请填写验证码！');
		return false;
	}}
	//return true;
}


	
	
$Login.do_parse_login_error = function(code){
	var $obj = $('span.login-process');
	switch(code){
		case '1':
			warning('邮箱或密码不能为空！')
			break;
		case '2':
			warning('验证码错误！');
			break;
        case '3':
            warning('邮箱未注册！<a href="/reg" style="color:blue;font-size:14px;">点击注册</a>');
            break;
        case '4':
            warning('密码有误，请您重新填写！');
            break;
        case '5':
            warning('用户不存在！');
            break;
	}
	function warning(value){
        $obj.html(value).css('color','red');	
	}
}
	
	
	



/*********** check avatar when use upload the picture *******************/
$Set.do_check_avatar = do_check_avatar = function(){
	var src = $("#file-avatar").val();
	var process = $('.self-upload-process');
    process.html('');
	if( src == ''){
		process.html('请选择图片！').css("color","red");
		return false;
	}
	var img_reg = /.*\.(jpg|png|jpeg|gif)$/ig;
	
	if(src.match(img_reg) == null ){
		process.html('图片格式为jpg,png,jpeg,gif！').css("color","red");
		return false;
	}
    $("#self-img-up-upb").attr("disabled","disabled").css("color","#ccc");
	return true;
}


/********* submit user crop ***********************/
$Set.do_crop_image = function(obj){
	var mes = $('#form-avatar').DivToDict();
	var process = $('#crop-process');
    process.html('');
	//alert(mes['pos-x']);
	//alert(mes['pos-y']);
	//alert(mes['pos-w']);

    $.postJSON("/crop-image", mes,
		function(){
			process.html('<img src="/static/img/ajax.gif" />');
	       $(obj).attr("disabled","disabled").css("color","#ccc");
	       $('button').attr("disabled","disabled").css("color","#ccc");
		},
		function(response){
		    if(response.kind == 0){
		         process.html('设置成功！').css('color','blue');
                 var tag = $("#feed-lib");
                 if(tag.html() != null){
                    // for group logo
                    setTimeout(location.href="/group-apply-lib", 1000);
                    $(obj).removeAttr("disabled").css("color","#555");	
                }else{
                    // for user avatar
                 //setTimeout($AFW_User.do_setting_open("content3"),1000);
                    //$(obj).removeAttr("disabled").css("color","#555");	
                 }
		    }else{
		          process.html(response.info);
		          $(obj).removeAttr("disabled").css("color","#555");	
		    }
		},
		function(response){
			process.html('提交失败!').css('color', 'red');
			$(obj).removeAttr("disabled").css("color","#555");	
		}	
	); 
    
}
	

button_enable = function(){
    $('button').removeAttr("disabled").css("color","#555");
}


/*********** init crop block **************/
$Set.do_crop_init = function(){
	  var jcrop_api, boundx, boundy;
	  
	   var $block = $('#crop-contain>img');
       var block_width = 0;
       var image_width = 0;
       var new_image = new Image();
	   new_image.src = $('#crop-contain>img').get(0).src;
	   $pos_x = $('#pos-x');
	   $pos_y = $('#pos-y');
	   $pos_w = $('#pos-w');
	   $pos_time = $('#pos-time');
	   $preview_120 = $('#preview-120');
	   $preview_50 = $('#preview-50');
	   $button = $('button.self-intro-button');
	   $process = $('#crop-process');
		
      $('#crop-obj').Jcrop({
        onChange: updatePreview,
        onSelect: updatePreview,
        aspectRatio: 1,
		minSize : [150,150],
		setSelect:[0,0,150,150],
		bgColor: 'black',
		maxSize:[400,400]
      },function(){
        // Use the API to get the real image size
        var bounds = this.getBounds();
        boundx = bounds[0];
        boundy = bounds[1];
        // Store the API in the jcrop_api variable
        jcrop_api = this;
      });

      function updatePreview(c)
      {
		
		
        if (parseInt(c.w) > 0)
        {
          var rx = 120 / c.w;
          var ry = 120 / c.h;

          $preview_120.css({
            width: Math.round(rx * boundx) + 'px',
            height: Math.round(ry * boundy) + 'px',
            marginLeft: '-' + Math.round(rx * c.x) + 'px',
            marginTop: '-' + Math.round(ry * c.y) + 'px'
          });
		
		var rx_1 = 50/c.w;
		var ry_1 = 50/c.h;
		 $preview_50.css({
            width: Math.round(rx_1 * boundx) + 'px',
            height: Math.round(ry_1 * boundy) + 'px',
            marginLeft: '-' + Math.round(rx_1 * c.x) + 'px',
            marginTop: '-' + Math.round(ry_1 * c.y) + 'px'
          });
        }
		
		$pos_x.val(c.x);
		$pos_y.val(c.y);
		$pos_w.val(c.w);
		
	    image_width = new_image.width;
	    block_width = $block.eq(0).width();
	    $pos_time.val('' + image_width/block_width);
	   //console.log(image_width/block_width);
	   //console.log(block_width);
	    $button.removeAttr('disabled').css('color', '#555');
		$process.html('裁剪后请提交！').css('color', 'black');
		//alert(c.w);
      };
}
	


/******* save self information****************/
$Set.do_save_info = function(obj){

    var process = $(obj).next();
    process.html('');
	var body = $.trim($("#self-name").val());
	
	var mes = {};
	mes['name'] = body;
	mes['type'] = 'info';

    if(mes['name'].length < 2){
        process.html('名字不能为一个字！').css('color','red');
        return false;
    }
    $.postJSON('/settings',mes,
			function(){ 
                process.html('<img src="/static/img/ajax.gif" />');
	            $(obj).attr("disabled","disabled").css("color","#ccc");    
             },
			function(response){
				if(response.kind == 0)
                {
                    process.html('修改成功！').css('color','blue'); 
                }else{
                    process.html(response.info).css('color','red'); 
                }
                $(obj).removeAttr("disabled").css("color","#555");
			},
			function(response){
				process.html('数据提交出错!');
			    $(obj).removeAttr("disabled").css("color","#555");
			}
	);	
}


/********** save password ********************/
$Set.do_save_password = function(obj){

    var process = $(obj).next();
    process.html('');
	//var body = $.trim($("#self-name").val());
	var old_pwd = $.trim($("#self-old-pwd").val());
    var new_pwd = $.trim($("#self-new-pwd").val());
    var pwd_again = $.trim($("#self-pwd-again").val());
	
	//mes['name'] = body;
    if(old_pwd.length < 4 || new_pwd.length < 4){
        process.html('密码至少四位！').css('color','red');
        return false;
    }	

    if(pwd_again != new_pwd){
        process.html('确认密码有误，请重新确认！').css('color','red');
        $("#self-pwd-again").val('');
        return false;
    }

    var mes = {};
    mes['old_pwd'] = old_pwd;
    mes['new_pwd'] = new_pwd;
    mes['type'] = 'password';

    $.postJSON('/settings',mes,
			function(){ 
                process.html('<img src="/static/img/ajax.gif" />');
	            $(obj).attr("disabled","disabled").css("color","#ccc");    
             },
			function(response){
				if(response.kind == 0)
                {
                    process.html('修改成功！').css('color','blue'); 
                    
                }else{
                    process.html(response.info).css('color','red');
                   
                }
                 $(obj).removeAttr("disabled").css("color","#555");
			},
			function(response){
				process.html('数据提交失败！');
			    $(obj).removeAttr("disabled").css("color","#555");
			}
	);	
}


$Set.do_save_intro = function(obj)
{
    var process = $(obj).next();
    process.html('');
    var textarea = $("#write_textarea");
	var body = $.trim($("#write_textarea").val());
	var pid = $("#write_menu").attr("article_id");
    var art_type = $("#write_menu").attr("article_type");
	
	var mes = {};
	mes['text'] = body;
	mes['article_id'] = pid;
    mes['article_type'] = art_type;
	
    $.postJSON('/update-article',mes,
			function(){ 
                process.html('<img src="/static/img/ajax.gif" />');
	            $(obj).attr("disabled","disabled").css("color","#ccc");    
             },
			function(response){
				if(response.kind == 0)
                {
                    process.html('更新成功！').css('color','blue');
                    $Write.close_window_close_alert();
                }else{
                    process.html(response.info).css('color','red');
                }
                //alert(0);
                 $(obj).removeAttr("disabled").css("color","black");
			},
			function(response){
				process.html('数据提交失败！');
			    $(obj).removeAttr("disabled").css("color","black");
			}
	);	

}


$Set.do_invite_friend = function(obj){
    var mes = $("#body_content").DivToDict();
    mes['type'] = 'invite';
    var $obj = $(obj);
    var $process = $obj.next();
    if(mes['email'] == ''){ $process.html('请您填写好友邮箱！').css('color','red'); return; }
    $.postJSON('/settings', mes, 
        function(){
            $process.html('<img src="/static/img/ajax.gif" />');
            $obj.attr('disabled','disabled').css('color', '#ccc');
        },
        function(response){
            if(response.kind==0){
                $process.html(response.info).css('color','blue');
            }else{
                $process.html(response.info).css('color','red');
                $obj.removeAttr('disabled').css('color','black');    
            }
        },
        function(){
            $process.html('数据提交出错！').css('color','red');
            $obj.removeAttr('disabled').css('color','black');         
        })
}


$Set.do_modify_domain = function(){
    var tag_html = [];
    tag_html.push('<div id="pop_insert_table">');
    tag_html.push("<p class='first'>个性化</p>");
    tag_html.push("<p>新链接后缀<input type='text' name='new_domain' /><input type='hidden' name='type' value='domain' />");
    tag_html.push("<p><button>修改</button><span class='t_process' style='width:70%'></span></p>");
    tag_html.push('</div>');
    _html = tag_html.join('');
    $html = jQuery(_html);
    pop_page(350,180, $html);
    $html.find('button').bind('click', function(){
        var mes = {}, $this=$(this), $process = $(this).next('.t_process'),regstr = /^[a-zA-Z0-9\.]+$/ig;
        mes = $('#pop_insert_table').DivToDict();
        if(mes['new_domain'] =='' || regstr.test(mes['new_domain']) == false ){
            $process.html('后缀为a-z，A-Z,0-9.').css('color','red');
            return false;        
        }
        $.postJSON('/settings', mes, function(){
            $process.html('<img src="/static/img/ajax.gif" />');
            $this.attr('disabled', 'disabled').css('color','#ccc');
        },
        function(response){
            if(response.kind==0){
                $process.html('修改成功！').css('color','blue');
                $('#body_content').find('div.my_domain').html('您的个性化链接为：http://www.afewords.com/me:' + mes['new_domain']);
                setTimeout(pop_page_close, 1000);            
            }else{
                 $this.removeAttr('disabled').css('color','black');
                 $process.html(response.info).css('color','red');             
            }
        },function(response){
            $this.removeAttr('disabled').css('color','black');
            $process.html(response.info).css('color','red');   
        })
    })
    .end().find('input').focus();
}







$AFW_User.get_feed_by_page = function(){
    var mes = {};
    mes['page'] = CURRENT_PAGE++;
    $.postJSON('/feed',mes,
		function(){ 
            _process = '<div id="feed" class="feed_process">'+
                            '<div class="f-body">'+
                            '<div class="f-con"><img src="/static/img/loading_bar.gif" /></div></div></div>';
            $("#left").append(_process);
        },
		function(response){
			if(response.kind == 0){
                _html = '<div id="feed-lib"><ul>';
                result = response.info;
                var ii = 0;
                for(ii in result){
                    tmp = result[ii];
                    _html += '<li>'+tmp.author_name+'<span style="margin:0 5px;">:</span>'+
                        '<a href="/blog/'+tmp.blog_id+'" target="_blank">'+tmp.title+'</a></li>';
                }
                _html += '<li><a href="/feed">更多...</a></li></ul></div>'
                $("#left").children(".feed_process").remove();
                $("#left").append(_html);
                
            }else{

            }
		},
		function(response){

		}
	);
}

});