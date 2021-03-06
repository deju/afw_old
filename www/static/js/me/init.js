jQuery(document).ready(function(){

jQuery.com = jQuery.com || {};
jQuery.com.afewords = jQuery.com.afewords || {};
jQuery.com.afewords.www = jQuery.com.afewords.www || {};
jQuery.com.afewords.www.user_page = jQuery.com.afewords.www.user_page || {};
jQuery.com.afewords.www.user_group = jQuery.com.afewords.www.user_group || {};
jQuery.com.afewords.www.user_write = jQuery.com.afewords.www.user_write || {};
jQuery.com.afewords.www.user_page = jQuery.com.afewords.www.user_page || {};
jQuery.com.afewords.www.user_blog = jQuery.com.afewords.www.user_blog || {};
jQuery.com.afewords.www.user_init = jQuery.com.afewords.www.user_init || {};
jQuery.com.afewords.www.user_settings = jQuery.com.afewords.www.user_settings || {};
jQuery.com.afewords.www.user_login = jQuery.com.afewords.www.user_login || {};

$Init = jQuery.com.afewords.www.user_init;
$Page = jQuery.com.afewords.www.user_page;
$Group = jQuery.afewords.user_group;
$Write = jQuery.com.afewords.www.user_write;
$Set = jQuery.com.afewords.www.user_settings;
$Login = jQuery.com.afewords.www.user_login;


jQuery.back_to_top();

/*** init every page ***/

/**** group create page ***/

$Init.init_group_create = function(){
    //alert($("#feed-lib").html());
    $("#group_create_table").find("button").bind('click', function(){
        $Group.group_create(this);
    });

};

$Init.init_group_set_logo =function(){
        $('form').submit(function(){  return $Set.do_check_avatar();   });
            $('#file-avatar').live('change', function(){
                $('span.self-upload-process').html('请选择图片！').css('color', 'black');
                $('#self-img-up-upb').removeAttr('disabled').css('color', '#555');
            });
            $('button.self-intro-button').live('click', function(){  $Set.do_crop_image(this); });
            $('#crop-contain>img').load(function(){  $Set.do_crop_init();  }).error(function(){
                $('#crop-process').html('图片加载失败！').css('color','red');    
            }); 
    /*
    $("body").find("#g-con:eq(0)").find("form").bind('submit', function(){
        $Set.do_check_avatar();
    });
    $("body").find("#g-con:eq(1)").find("button").bind('click', function(){
        $Set.do_crop_avatar(this); 
    })
    $Set.do_crop_init(); */
}

$Init.init_reg = function(){
    var target = $("#login");
    var email = getQueryStringRegExp('email');
    if( email != '') $("#login-email").val(email);
    var submit_button = target.find("button");
    submit_button.bind('click', function(){
          $Login.do_reg(this);
    }); 
    $('#login').find('a.code_change').bind('click', function(){
         $Tool.change_code();
         return false;
    });   
}
$Init.init_reset_page = function(){
    $('button.login_button').bind('click', function(){
           $Login.do_reset_password(this);
    });
    $('#login').find('a.code_change').bind('click', function(){
         $Tool.change_code();
         return false;
    });  
}

$Init.init_login_do_page = function(){
    var email = getQueryStringRegExp('email');
    var error_code = getQueryStringRegExp('error');

    if( email != '') $("#login-email").val(email);

    if(error_code != ''){
        $Login.do_parse_login_error(error_code);
    }
     $('#login').find('a.code_change').bind('click', function(){
         $Tool.change_code();
         return false;
    });  
}

$Init.init_login_page = function(){
    $('form.index-login').submit(function(){
        return $Login.do_login_check();    
    });
}


$Init.init_settings_page = function(kind){
    var $target = $("#body_content");
    switch(kind){
        case 'password':
            $target.find("button").die().bind('click', function(){
                $Set.do_save_password(this);
                return false;
            });
            break;
        case 'avatar':
            $('form').submit(function(){  return $Set.do_check_avatar();   });
            $('#file-avatar').live('change', function(){
                $('span.self-upload-process').html('请选择图片！').css('color', 'black');
                $('#self-img-up-upb').removeAttr('disabled').css('color', '#555');
            });
            $('button.self-intro-button').live('click', function(){  $Set.do_crop_image(this); });
            $('#crop-contain>img').load(function(){  $Set.do_crop_init();  }).error(function(){
                $('#crop-process').html('图片加载失败！').css('color','red');    
            });
            break;
        case 'tag':
            $('span.tag_new').live('click', function(){ $Write.new_tag('settings-tag'); });
            $('span.tag-del').live('click', function(){
                $Write.delete_tag_submit(this);
            });
            $target.find('li').live('mouseover', function(){ $(this).children('.tag-del').show(); }).
                live('mouseout', function(){ $(this).children('.tag-del').hide(); });
            break;
        case 'like':
            $target.find('li').live('mouseover', function(){ $(this).children('.like_cancel').show() })
                .live('mouseout', function(){ $(this).children('.like_cancel').hide(); })
                    .find('.like_cancel').click(function(){ do_like(this); });
            break;
        case 'follow':
        case 'follower':
            $target.find('a.follow_cancel').click(function(){ do_follow(this); });
            break;
        case 'about':
            var about_button = $target.find('button');
            about_button.bind('click', function(){  $Set.do_save_intro(this);  });
            $("#write_textarea").bind('change', function(){
                about_button.next('span').html('');
            });
            break;
        case 'invite':
            var invite_button = $target.find('button');
            invite_button.click(function(){ $Set.do_invite_friend(this); });
        case 'domain':
            $('#body_content').find('.page_nav').find('.domain').click(function(){
                $Set.do_modify_domain();            
            });
        default:
            break;    
    
    }

}

$Init.init_author_page = function(){
    $('div.user_control').find('span').click(function(){ do_follow(this); });
    $('div.like').find('li').live('mouseover', function(){ $(this).children('.like_cancel').show() })
                .live('mouseout', function(){ $(this).children('.like_cancel').hide(); })
                    .find('.like_cancel').click(function(){ do_like(this); });
};
$Init.init_follow_page =function(){
    $('div.follow_one').find('.control').find('a').click(function(){ do_follow(this); });
}


$Init.init_blog_lib_page = function(){
   $('#body_content').find('li').live(
        'mouseover',function(){
        $(this).children(".blog_edit").show();
    }).live('mouseout', function(){
        $(this).children(".blog_edit").hide();
    }) 
}
$Init.init_draft_page = function(){
    $('#body_content').find('li').live(
        'mouseover',function(){
        $(this).children(".draft_del").show();
    }).live('mouseout', function(){
        $(this).children(".draft_del").hide();
    });
}

$Init.init_write_page = function(){
      var write_height = $(document).height();
	    if(write_height < 600)
			write_height = 600;
	   $(".text").css({"height":(500) + "px","resize":"none"});
	   $('div.w-open').children('span').bind('click', function(){   $Write.write_toggle_title(this); });
	   $('div.w-preview').children('button').bind('click', function(){$Write.post_write_all(this); });
	   $('div.w-submit').children('button').bind('click', function(){ $Write.post_write_all(this); });
	   $('div.w-class').find('span.cursor-pointer').bind('click', function(){ $Write.new_tag(); });
	   $('#head').slideUp('slow');
	   $('#footer').hide();
}

$Init.init_notice_page = function(){
    $('#body_content').find('a.noti_link').live('click', function(){
        $Control.do_noti_flag_set(this);
        return true;   
    });
}

$Init.init_blog_page = function(){
    //document.body.style.backgroundColor='#f8f8f8';
    $('.bot-comment').bind('click', function(){
        $Write.comment_create(this);
    });
    $('span.blog_tip_comment').find('.blog_tip_do').bind('click', function(){
        $Write.comment_create(this);
    });
    $('span.blog_tip_like').find('.blog_tip_do').bind('click', function(){
        do_like(this);    
    });
    $('span.blog_tip_star').find('a').bind('click', function(){
        $Write.recommend_to_book(this);    
    });
    function do_view(){
        $obj = $('span.blog_tip_view');
        do_like($obj[0]);
    }
    setTimeout(do_view, 7000);
    
    $('span.blog_tip_view').bind('click', function(){
        do_like(this);    
    });
    $('div.blog_tip').bind({
    'mouseover': function(){
        $(this).find('.blog_tip_do').show();    
    },
    'mouseout':function(){
        $(this).find('.blog_tip_do').hide();    
    }
    });
}


$Init.init_group_write = function(){
    $('button.self-intro-button').click(function(){
        $Write.group_write_post();
    });    
}

$Init.init_group_doc_lib_page = function(){
    $('span.add_tag').find('a').live('click', function(){ $Write.new_tag('group-tag', this); });
    $('a.del_tag').live('click', function(){
         $Write.delete_tag_submit(this);
    });
    $('div.board_con').find('span').live('mouseover', function(){ $(this).children('a.del_tag').show(); }).
        live('mouseout', function(){ $(this).children('a.del_tag').hide(); });
    /*
    $target.find('li').live('mouseover', function(){ $(this).children('.tag-del').show(); }).
       live('mouseout', function(){ $(this).children('.tag-del').hide(); });*/
}

$Init.init_all =function(){
    var href_string = location.pathname;
    var page_height = jQuery(window.document).height();
    var head_height = $("#head").height();
    var footer_height = $("#footer").height();
    var middle_height = $("#middle").height();
    var want_height = page_height - footer_height - head_height;
    //console.log(footer_height)
    if(middle_height < want_height){
        $("#middle").css("min-height",''+ want_height -10 + "px");
    }    
    if(href_string.search('/reg') != -1 || href_string.search('/') != -1 ||
        href_string.search('/reset') != -1 || href_string.search('/login') != -1){
        if(page_height < window.screen.availHeight){
            var login_do_height = want_height - 50;
            var login_height = $('#login_do').height();
            $('#login_do').css('margin-top', (login_do_height-login_height)/3 + "px");
        }else{
            $('#afw_info').css('height','300px');        
        }
        setTimeout(afewords_marquee, 2000);
        
    }
    if(href_string.search('/settings')!=-1){
    if(settings_type){
        var $top_nav_a = $('#top_nav').find('a');
        if($top_nav_a.length > 0){
            
            $Init.init_settings_page(settings_type);
            return;
        }
        
        
    }};
    
    if(href_string.search('/bloger') != -1 || 
        href_string.search('/follow') !=-1 || 
        href_string.search('/about') != -1 || 
        href_string.search('/like') != -1)
    {
        $Init.init_author_page();
        //return;    
    }
    if(href_string.search('/follow') != -1 || href_string.search('/user-lib') != -1){
        $Init.init_follow_page();
        return;    
    }
  
    
    if(href_string.search('/group-set-logo')!=-1){
        $Init.init_group_set_logo();
        return ;
    }

    if(href_string.search('/group-create')!=-1){
        $Init.init_group_create();
        return ;
    }
    if(href_string.search('/group/') != -1 || href_string.search('/group-edit/') != -1){
        $Init.init_group_doc_lib_page();
        $Init.init_group_write();
        $('span.bot-comment').bind('click', function(){
            $Write.comment_create(this);
        });    
    }

    if(href_string.search('/write')!=-1){
        //  write blog page init 
       $Init.init_write_page();
       return;
    };
    
    if(href_string.search('/reset')!=-1){
        // reset password page 
        $Init.init_reset_page();
        return;
    }
    if(href_string.search('/reg') != -1){
            $Init.init_reg();
            return;
    }
    
    if(href_string.search('/login') != -1){
        $Init.init_login_do_page(); 
        return;   
    }

    
    if(href_string.search('/blog-lib') != -1){
        $Init.init_blog_lib_page();
        return;    
    }
    
    if(href_string.search('/notice') != -1){
        $Init.init_notice_page();
        //console.log('init notice');
        return;    
    } 
    
    if(href_string.search('/draft') != -1){
        $Init.init_draft_page();
        return;    
    }   
    
    if(href_string.search('/blog') != -1){
        $Init.init_blog_page();    
        return;
    }
    
    if(href_string.search('/') != -1){
        // have bug 
        $Init.init_login_page();    
        //alert(href_string);
        return;
    }
}

$Init.init_all();







});