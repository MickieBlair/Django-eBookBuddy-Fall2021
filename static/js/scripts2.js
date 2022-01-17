console.log("Scripts Loading....");
console.log("Loading Server Clock Script...")
// *** URL For AJAX Requests
var url_full = ""

function get_url(url_base) {
  console.log("get_url")
  // event.preventDefault();
  url_full = url_base
  console.log(url_full)
};

const initial_entry_link = document.getElementById('initial_entry_link')
// console.log("Entry Link", initial_entry_link)
const landing_link = document.getElementById('landing_link')
// console.log("Landing Link", landing_link)
const clock_div = document.getElementById('server_clock')
let member_role = ""

if(document.getElementById('user_role')){
  member_role = JSON.parse(document.getElementById('user_role').textContent);
  // console.log("member_role", member_role)
}

if(document.getElementById('orientation_today')){
let js_orientation_date = ""
const orientation_today = JSON.parse(document.getElementById('orientation_today').textContent);
const show_orientation_button = JSON.parse(document.getElementById('show_orientation_button').textContent);
const day_with_o_meeting_date = JSON.parse(document.getElementById('day_with_o_meeting_date').textContent);
const day_with_o_meeting_time_start = JSON.parse(document.getElementById('day_with_o_meeting_time_start').textContent);
const day_with_o_meeting_time_end = JSON.parse(document.getElementById('day_with_o_meeting_time_end').textContent);
// console.log("orientation_today", orientation_today)
// console.log("show_orientation_button", show_orientation_button)
// console.log("day_with_o_meeting_date", day_with_o_meeting_date)
// console.log("day_with_o_meeting_time_start", day_with_o_meeting_time_start)
// console.log("day_with_o_meeting_time_end", day_with_o_meeting_time_end)

if(orientation_today){
  let split_date = day_with_o_meeting_date.split('-')
  // console.log("split_date", split_date)
  let year = parseInt(split_date[0])
  let monthIndex = parseInt(split_date[1]) - 1
  let day = parseInt(split_date[2])
  // console.log("split_date year", year)
  // console.log("split_date month", monthIndex)
  // console.log("split_date orientation_today", day)
  js_orientation_date = new Date(year, monthIndex, day)
  
}
}


if (clock_div){

  const entry_start = JSON.parse(document.getElementById('entry_start').textContent);
  const entry_end = JSON.parse(document.getElementById('entry_end').textContent);
  console.log("entry_start", entry_start)
  console.log("entry_end", entry_end)
  const entry_start_hour =entry_start.split(":")[0]
  const entry_start_min =entry_start.split(":")[1]
  const entry_start_sec =entry_start.split(":")[2]
  const entry_end_hour =entry_end.split(":")[0]
  const entry_end_min =entry_end.split(":")[1]
  const entry_end_sec = entry_end.split(":")[2]

  setInterval(showTime, 1000); 

  function showTime() { 

    var dt = new Date();
    // console.log("initial",dt); // Gives Tue Mar 22 2016 09:30:00 GMT+0530 (IST)

    dt.setTime(dt.getTime()+dt.getTimezoneOffset()*60*1000);
    // console.log("next",dt); // Gives Tue Mar 22 2016 04:00:00 GMT+0530 (IST)
    var offset = JSON.parse(document.getElementById('offset').textContent);
  
    var estDate = new Date(dt.getTime() + offset*60*1000);
    // console.log("eastern", estDate); //Gives Mon Mar 21 2016 23:00:00 GMT+0530 (IST)


    // let time = new Date(); 
    let time = estDate;
    // console.log("Time", time)
    let hour = time.getHours();
    // console.log(hour)
    let base_hour = time.getHours(); 
    let min = time.getMinutes(); 
    let base_min = time.getMinutes(); 
    let sec = time.getSeconds();
    let base_sec = time.getSeconds();  
    am_pm = "AM"; 
    
    if (hour > 12) { 
        hour -= 12; 
        am_pm = "PM"; 
    } 
    else if (hour == 0) { 
        hr = 12; 
        am_pm = "AM"; 
    } 

    else if (hour == 12) { 
        // hour -= 12; 
        am_pm = "PM"; 
    } 

  
    hour = hour < 10 ? "0" + hour : hour; 
    min = min < 10 ? "0" + min : min; 
    sec = sec < 10 ? "0" + sec : sec; 
  
    let currentTime = hour + ":" 
            + min + ":" + sec + " " + am_pm; 
              
    document.getElementById("server_clock").innerHTML = currentTime;
    // console.log("member_role", member_role)
  
    if (base_hour == entry_start_hour){
      if (base_min == entry_start_min){
        if (base_sec == entry_start_sec){
          // ajax_check_jitsi()
          if(member_role == "Student"){
            // console.log("Student Entry Allowed")
            // initial_entry_link.click()
            landing_link.click() 
          } else if (member_role == "Volunteer"){
            // console.log("Volunteer Entry Allowed")
            landing_link.click() 
          }
          
        }
      }

    }

    if (base_hour == entry_end_hour){
      if (base_min == entry_end_min){
        if (base_sec == entry_end_sec){
          // ajax_check_jitsi()
          if(member_role == "Student"){
            // console.log("Student Entry Allowed End")
            landing_link.click()            
          }else if (member_role == "Volunteer"){
            // console.log("Volunteer Entry Allowed End")
            landing_link.click() 
          }
          
        }
      }
    }

  } 
showTime();   
}


