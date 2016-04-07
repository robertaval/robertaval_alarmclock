
<!-- the toggle button that toggles a static or edit section -->
      <input class="editing_alarm_chk" id="{{alarm_id}}_editing" type="checkbox" onchange="action('update', '{{alarm_id}}')">
      <label for="{{alarm_id}}_editing" class="editing_alarm"> </label>

<!-- the static section -->
      <div class="alarm_static_frame">
        <label><input type="checkbox" name="active" value="active" {{active}} disabled>
        <span class="chk_active"></span></label>
        <p class="time">{{time}}</p>
        <p class="static_subscript">{{alarm_id}} on {{days}}</p>
      </div>

<!-- the dynamic section-->

      <div class="alarm_edit_frame">
          <form id="{{alarm_id}}_form">
          <div class="times_span">

    <!-- time and name -->
          <label><input type="checkbox" name="active" value="active" {{active}}>
            <span class="chk_active"></span></label>
          <input type="hidden" name="alarm_id" value="{{alarm_id}}">
          <input type="time" class="time" name="time" value="{{time}}">
          <input type="text" id="{{alarm_id}}_name" name="name" value="{{name}}">
        </div>
    <!-- days of week -->
        <div class="repeating_div">
            <input id="{{alarm_id}}_rep" class="rep_checkbox" type="checkbox" name="repeating" value="repteating" {{repeating}}>
          <label class="check_box alarm_icons chk_repeating" for="{{alarm_id}}_rep"></label>
          <span class="days_span">
          <label>
             <input type="checkbox" name="day" value="MO" {{MO}}>
             <span class="days check_box">MO</span></label>
          <label>
            <input type="checkbox" name="day" value="TU" {{TU}}>
            <span class="days check_box">TU</span></label>
          <label>
            <input type="checkbox" name="day" value="WE" {{WE}}>
            <span class="days check_box">WE</span></label>
          <label>
            <input type="checkbox" name="day" value="TH" {{TH}}>
            <span class="days check_box">TH</span></label>
          <label>
            <input type="checkbox" name="day" value="FR" {{FR}}>
            <span class="days check_box">FR</span></label>
          <label>
            <input type="checkbox" name="day" value="SA" {{SA}}>
            <span class="days check_box">SA</span></label>
          <label>
            <input type="checkbox" name="day" value="SU"{{SU}}>
            <span class="days check_box">SU</span></label>
          </span>
          <span class="date_span">
                <input type="date" name="date" min={{min_date}} value="{{date}}">
              </span>
        </div>
    <!-- a few other buttons -->
        <div class="buttons_span">
          <a href="#" onclick="action('delete', '{{alarm_id}}')">
            <span class="button_delete alarm_icons"></span></a>

           <label class="color_button">
             <div><input type="color" name="color" value="#{{color}}">
             <span>color</span></div>
           </label>
        </div>
        </form>
      </div>
