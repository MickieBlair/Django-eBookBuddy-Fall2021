console.log("Loading Reading Session Scripts");


let send_private_message_to = ""
$('#id_to_user')
        .editableSelect()
        .on('select.editable-select', function (e, li) {
            // console.log('Seletced Value: ');
            // console.log(li.val() + '. ' + li.text());
            if(li){
               send_private_message_to = li.val()
                focus_on_content() 
            }
            

    });


function clear_editable_select_to_user(){
    // console.log("Here")
    $('#id_to_user')
        .editableSelect('destroy');
    // select_to_input.editableSelect('clear');
    $('#id_to_user')
        .editableSelect()
        .on('select.editable-select', function (e, li) {
            // console.log('Seletced Value: ');
            // console.log(li.val() + '. ' + li.text());
            if(li){
                send_private_message_to = li.val()
                focus_on_content()
            }

    });
}



const chat_message_input = document.getElementById('id_chat_message_input')

const monitoring_div = document.getElementById('staff_left_panel')
const drag_div = document.getElementById('staff_drag')
const video_div = document.getElementById('staff_right_panel')

const all_sessions_div = document.getElementById('all_sessions_div')
const matches_in_session_div = document.getElementById('matches_in_session')
const staff_chat_message_input = document.getElementById('staff_chat-message-input')
const private_message_to_input = document.getElementById('id_to_user')

function determine_button(element){
    // console.log("determine_button",element);
    let element_id = element.getAttribute('id')
    const all_monitoring_divs = document.querySelectorAll('.monitoring_type');
    // console.log("all_monitoring_divs", all_monitoring_divs)

    for (let item of all_monitoring_divs){
        item.style.display = "none";
    }

    let str_left = adjusted_left_panel_width + "px"
    let str_right = adjusted_right_panel_width + "px"
    
    monitoring_div.style.display = "flex";
    monitoring_div.style.width = str_left;
    drag_div.style.display = "flex";
    video_div.style.width = str_right;

    let id_to_display = element_id + "_show"
    // console.log(id_to_display);

    let element_to_display = document.getElementById(id_to_display)
    element_to_display.style.display="block";
    if (id_to_display == "todays_session_btn_show"){
        all_sessions_div.style.display = "block";   
        matches_in_session_div.style.display = "none";
    }
    else if(id_to_display == "staff_chat_btn_show"){
        staff_chat_message_input.focus();
        let staff_reset_count = document.getElementById('staff_reset_count')
        staff_reset_count.click()
    }
    else if(id_to_display == "room_chat_btn_show"){
        chat_message_input.focus();
        ajax_room_reset()
    }
    else if(id_to_display == "staff_messages_btn_show"){
        

    }
    
};

function determine_session(element){
    all_sessions_div.style.display = "none";   
    matches_in_session_div.style.display = "block";

    const outer_session_divs = document.querySelectorAll('.outer_session_div');
    let id_for_outer_div_show = "outer_session_div_" + element.getAttribute("value")

    for (let item of outer_session_divs) {
        if (item.id == id_for_outer_div_show){
         item.style.display = "block";
        } else {
         item.style.display = "none";
        }
    }
}

function close_monitoring(element){
    monitoring_div.style.display = "none";
    // monitoring_div.style.width = "50%";
    drag_div.style.display = "none";
    video_div.style.width = "100%";
    // ajax_room_reset()
    // let room_chat_btn_show = document.getElementById('room_chat_btn_show')
    // room_chat_btn_show.style.display="none";
}

// non_staff functions





function close_left_pane(button_element){
  left_pane_non_staff.style.display = "none";
  room_chat_div_non_staff.style.display="none";
  private_msgs_div_non_staff.style.display = "none";
}


// Open-Close Full Screen
const open_full_screen_btn = document.getElementById('open_full_screen');
const close_full_screen_btn = document.getElementById('close_full_screen');

/* Get the documentElement (<html>) to display the page in fullscreen */
var elem = document.documentElement;

/* View in fullscreen */
function open_full_screen() {

  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.webkitRequestFullscreen) { /* Safari */
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) { /* IE11 */
    elem.msRequestFullscreen();
  }

  open_full_screen_btn.style.display = "none";
  close_full_screen_btn.style.display = "inline-grid";
}

/* Close fullscreen */
function close_full_screen() {
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if (document.webkitExitFullscreen) { /* Safari */
    document.webkitExitFullscreen();
  } else if (document.msExitFullscreen) { /* IE11 */
    document.msExitFullscreen();
  }

  open_full_screen_btn.style.display = "inline-grid";
  close_full_screen_btn.style.display = "none";
}

document.addEventListener('fullscreenchange', exitHandler);
document.addEventListener('webkitfullscreenchange', exitHandler);
document.addEventListener('mozfullscreenchange', exitHandler);
document.addEventListener('MSFullscreenChange', exitHandler);

function exitHandler() {
    if (!document.fullscreenElement && !document.webkitIsFullScreen && !document.mozFullScreen && !document.msFullscreenElement) {
        open_full_screen_btn.style.display = "inline-grid";
        close_full_screen_btn.style.display = "none";
    }
} 



let overall_window_width = $(window).width();
let adjusted_left_panel_width = overall_window_width/2
let adjusted_right_panel_width = overall_window_width/2
var onresize = function(e) {
   overall_window_width = e.target.outerWidth;
   // console.log('overall_window_width', overall_window_width)

}
window.addEventListener("resize", onresize);




// function close_people_in_room(button_element){
    
// }

// function click_profile_modal(id_to_click){
//     console.log("clicking profile modal", id_to_click)
// }



//Resizing Staff panes

let isResizing = false;
let lastDownX = 0;

$(function () {
    let container = $('#staff_outer_div')
    let staff_sidebar = $('#staff_sidebar')
    let staff_left_panel = $('#staff_left_panel')
    let room_header_inline_grid = $('#room_header_inline_grid')
    let unmatched_row = $('#unmatched_row')
    let monitoring_content = $('#monitoring_content')
    let staff_right_panel = $('#staff_right_panel')
    let handle = $('#staff_drag')

    var window_width = $(window).width();
    // console.log('window_width', window_width);

    var container_width = container.width();
    // console.log('container_width', container_width);

    var sidebar_width = staff_sidebar.width();
    // console.log('sidebar_width', sidebar_width);

    var staff_left_panel_width = staff_left_panel.width();
    // console.log('staff_left_panel_width', staff_left_panel_width);   

    
    var staff_right_panel_width = staff_right_panel.width();
    // console.log('staff_right_panel_width', staff_right_panel_width);
    
    


    if(container){

        // $(handle).mouseenter(function(){isResizing=true;});
        // $(handle).mouseleave(function(){isResizing=false;});
        
        //console.log('isResizing', isResizing);
        //console.log('lastDownX', lastDownX);

        handle.on('mousedown', function (e) {
        isResizing = true;
        lastDownX = e.clientX;

            // console.log('Mouse down isResizing', isResizing);
            // console.log('mouse down lastDownX', lastDownX);
        });

        $(document).on('mousemove', function (e) {
            // console.log("Doing something")
            
            // we don't want to do anything if we aren't resizing.
            if (!isResizing) 
                return;

            lastDownX = e.clientX;

            var room_header_inline_grid_height = room_header_inline_grid.height();
            // console.log('room_header_inline_grid_height', room_header_inline_grid_height);

            var unmatched_row_height = unmatched_row.height();
            // console.log('unmatched_row_height', unmatched_row_height);

            let header_height = room_header_inline_grid_height + unmatched_row_height + 5
            // console.log('header_height', header_height);

            let height_str = "calc(100% - " + header_height + "px)"

            monitoring_content.css('height', height_str);

            // console.log('mouse_moving', lastDownX);
            var container_width = container.width();
            // console.log('container_width', container_width);

            var sidebar_width = staff_sidebar.width();
            // console.log('sidebar_width', sidebar_width);

            
            var left_width = lastDownX//- (e.clientX - container.offset().left);
            adjusted_left_panel_width = left_width;
            // console.log('left_width', left_width);

            var right_width = container_width -  lastDownX //- (e.clientX - container.offset().left);
            adjusted_right_panel_width = right_width;
            // console.log('right_width', right_width);

            if(right_width <= 225){
                let set_panel_width = container_width - 225;
                let width_str = set_panel_width + 'px'
                staff_left_panel.css('width', width_str);
                staff_right_panel.css('width', '225px');
            } else {
                staff_left_panel.css('width', left_width);
                staff_right_panel.css('width', right_width);
            }

        }).on('mouseup', function (e) {
            // stop resizing
            isResizing = false;

            //console.log('Mouse up isResizing', isResizing);
            //console.log('mouse up lastDownX', lastDownX);
        });
    };
});