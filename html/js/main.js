function setup() {
  html = "";
  $.ajax({
    url:"/sprinkers",
    type:"GET",
  }).done(function(e, data){
    document.location.reload();
  }).fail(function(e, data) {

<?php printf('<div style="display: none" id="sprinkler%d">', $i); ?>
      <?php printf('<button id="override%d">Manual</button>', $i); ?>
      <?php printf('<button id="toggle%d">Enable</button>', $i); ?>
      <?php printf('<span class="name">%s</span>', $aName[$i]); ?>
      Runtime
      <?php printf('<select id="runtime%d">', $i); ?>
        <option value="1">1 minute</option>
        <option value="5">5 minutes</option>
        <option value="10">10 minutes</option>
        <option value="15">15 minutes</option>
      </select>
      Cycles
      <?php printf('<select id="cycles%d">', $i); ?>
        <option value="1">Once</option>
        <option value="2">Twice</option>
        <option value="3">Trice</option>
      </select>
      Every
      <?php printf('<select id="stepping%d">', $i); ?>
        <option value="1">day</option>
        <option value="2">other day</option>
        <option value="3">3rd day</option>
        <option value="4">4th day</option>
        <option value="5">5th day</option>
        <option value="6">6th day</option>
        <option value="7">7th day</option>
        <option value="8">8th day</option>
        <option value="9">9th day</option>
        <option value="10">10th day</option>
        <option value="11">11th day</option>
        <option value="12">12th day</option>
        <option value="13">13th day</option>
        <option value="14">14th day</option>
      </select>
    </div>

}
