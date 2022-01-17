console.log("Admin Scripts Loading");
let total_users = 0

// *** URL For AJAX Requests
var url_full = ""

function get_url(url_base) {
  console.log("get_url")
  // event.preventDefault();
  url_full = url_base
  console.log(url_full)
};

function display_all_users() {
  let results_count = document.getElementById('results_count')
            results_count.innerHTML = total_users
   let all_users = document.querySelectorAll('.user_row')
            for(let item of all_users){
              item.style.display="table-row"
            }
}

$(".ajax_search_users").click(function(e){
    console.log("AJAX Searching Users")
    e.preventDefault();
    
    let search_terms_element = document.getElementById('search_terms')
    let search_terms = search_terms_element.value
    console.log("Search Terms", search_terms)

    let role_input_element = document.getElementById('role_input')
    let role_on_page = role_input_element.value
    console.log("Role ", role_on_page)

   if (search_terms != ""){
        $.ajax({
        type: 'GET',
        url: url_full,
        data: {"search_terms": search_terms, "role": role_on_page },
        success: function (response) {
          if(response["valid"]){
            console.log(response)
            // response['total_users'] = total_users.count()
      // response['results_id_list'] = results_id_list
            
            let results_count = document.getElementById('results_count')
            results_count.innerHTML = response['count'] 

            total_users = response['total_users']

            let all_users = document.querySelectorAll('.user_row')
            for(let item of all_users){
              item.style.display="none"
            }

            let result_users = response['results_id_list']
            for(let user of result_users){

              let user_row_id = document.getElementById('user_report-'+ user)
              user_row_id.style.display = "table-row"
            }
            // "student_user_report-{{student.id}}"
            search_terms_element.value=""
                   
          }
        },
        error: function (response) {
            console.log(response)
        }
      });

   };


  });

$(".approve_user").click(function(e){
    e.preventDefault();

    const target_id = e.target.value;
    const checkbox_id = $('#' + e.target.id);
    const last_updated_id = $('#last_updated-' + target_id)
    // console.log("1", last_updated_id.text());

    $.ajax({
      type: 'GET',
      url: url_full,
      data: {"target_id": target_id},
      success: function (response) {
        if(response["valid"]){
        	if(response.status){
        		checkbox_id.prop("checked", true);
        	}else{
        		checkbox_id.prop("checked", false)
        	}

        	date_now = new Date()
        	// console.log("date_now", date_now)
        	last_updated_id.text(date_now.toLocaleString())               
        }
      },
      error: function (response) {
          console.log(response)
      }
    })
  });


$(".mark_session_complete").click(function(e){
    e.preventDefault();

    const target_id = e.target.value;
    const checkbox_id = $('#' + e.target.id);
    const last_updated_id = $('#session_last_updated-' + target_id)

    $.ajax({
      type: 'GET',
      url: url_full,
      data: {"target_id": target_id},
      success: function (response) {
        if(response["valid"]){
          if(response.status){
            checkbox_id.prop("checked", true);
          }else{
            checkbox_id.prop("checked", false)
          }

          date_now = new Date()
          // console.log("date_now", date_now)
          last_updated_id.text(date_now.toLocaleString())               
        }
      },
      error: function (response) {
          console.log(response)
      }
    })

  });

$(".mark_session_complete_home").click(function(e){
  console.log(window.location)
    e.preventDefault();

    // const target_id = e.target.value;
    // const checkbox_id = $('#' + e.target.id);
    // const last_updated_id = $('#session_last_updated-' + target_id)
    // let input_box = document.getElementById(e.target.id);
    // console.log('input_box', input_box)
    // if(input_box.checked){
    //       $.ajax({
    //       type: 'GET',
    //       url: url_full,
    //       data: {"target_id": target_id},
    //       success: function (response) {
    //         if(response["valid"]){
    //           if(response.status){
    //             checkbox_id.prop("checked", true);
    //           }else{
    //             checkbox_id.prop("checked", false)
    //           }

    //           date_now = new Date()
    //           // console.log("date_now", date_now)
    //           last_updated_id.text(date_now.toLocaleString())               
    //         }
    //       },
    //       error: function (response) {
    //           console.log(response)
    //       }
    //     }).done(function() {
    //         location.reload();
    //       });
    // }else{
    //   console.log('not checked remove after testing')
    //             $.ajax({
    //       type: 'GET',
    //       url: url_full,
    //       data: {"target_id": target_id},
    //       success: function (response) {
    //         if(response["valid"]){
    //           if(response.status){
    //             checkbox_id.prop("checked", true);
    //           }else{
    //             checkbox_id.prop("checked", false)
    //           }

    //           date_now = new Date()
    //           // console.log("date_now", date_now)
    //           last_updated_id.text(date_now.toLocaleString())               
    //         }
    //       },
    //       error: function (response) {
    //           console.log(response)
    //       }
    //     }).done(function() {
    //         location.reload();
    //       });
    // }

    

  });


function open_number_of_sections_div(element){
  let div_for_num_of_section = 'num_of_sections-'+ element.value
  
  let div_to_display = document.getElementById(div_for_num_of_section)
  console.log(div_to_display.style)
  if (div_to_display.style.display == "none"){
    div_to_display.style.display = "block"
  } else if (div_to_display.style.display == "block"){
    div_to_display.style.display = "none"
  } else{
    console.log("Else")
  }
}
function session_day_time(name, num){
  let form_day_time_div = document.createElement('div');
  let session_slot = document.createElement('input')
  session_slot.setAttribute('name', name + "-" + num)
  form_day_time_div.append(session_slot);

  return form_day_time_div
}

function changing_session_number(element){
  console.log("element", element, element.value);
  let div_id = element.name.split('-')[0] + "-form";
  console.log('div_id', div_id);
  let div_to_add_session_forms = document.getElementById(div_id)
  console.log("div_to_add_session_forms", div_to_add_session_forms)

  for (i = 0; i < element.value; i++) {
    console.log("The number is " + i);
    div_to_add_session_forms.append(session_day_time(element.name.split('-')[0]), i+1)
  }
}

function clear_error(){
  let errors = document.querySelectorAll(".error_form")
  for(let item of errors){
    item.remove()
  }
}

function show_student_profile(element){
  console.log(element);
}

function clear_errorlist(){
  console.log("clicking")
  let errors = document.querySelectorAll(".error_list")
  for(let item of errors){
    item.remove()
  }
}

