function generateSprinkler(sprinkler)
{
  html  = '<div id="sprinkler' + sprinkler.id + '">';
  html += '<button id="delete' + sprinkler.id + '">Delete</button>';
  html += '<button id="override' + sprinkler.id + '">Manual</button>';
  html += '<button id="toggle' + sprinkler.id + '">Enable</button>';
  html += '<span class="name">' + sprinkler.name + '</span>';
  html += 'Runtime';
  html += '<select id="runtime' + sprinkler.id + '">';
  html += '<option value="1">1 minute</option>';
  html += '<option value="5">5 minutes</option>';
  html += '<option value="10">10 minutes</option>';
  html += '<option value="15">15 minutes</option>';
  html += '</select>';
  html += 'Cycles';
  html += '<select id="cycles' + sprinkler.id + '">';
  html += '<option value="1">Once</option>';
  html += '<option value="2">Twice</option>';
  html += '<option value="3">Trice</option>';
  html += '</select>';
  html += 'Every';
  html += '<select id="stepping' + sprinkler.id + '">';
  html += '<option value="1">day</option>';
  html += '<option value="2">other day</option>';
  html += '<option value="3">3rd day</option>';
  html += '<option value="4">4th day</option>';
  html += '<option value="5">5th day</option>';
  html += '<option value="6">6th day</option>';
  html += '<option value="7">7th day</option>';
  html += '<option value="8">8th day</option>';
  html += '<option value="9">9th day</option>';
  html += '<option value="10">10th day</option>';
  html += '<option value="11">11th day</option>';
  html += '<option value="12">12th day</option>';
  html += '<option value="13">13th day</option>';
  html += '<option value="14">14th day</option>';
  html += '</select>';
  html += '</div>';
  return html;
}

function setup() {
  html = "";
  $.ajax({
    url:"/sprinklers",
    type:"GET",
  }).done(function(e, data){
    for (s in e) {
      s = e[s];
      console.log(s);
      html += generateSprinkler(s);
    }
    $('#list').html(html);
  }).fail(function(e, data) {
    alert('Unable to load sprinklers')
  });
}

