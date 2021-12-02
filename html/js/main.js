/**
  * This file is part of rainfall (https://github.com/mrworf/rainfall).
  *
  * rainfall is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  *
  * rainfall is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with rainfall.  If not, see <http://www.gnu.org/licenses/>.
  */
function loadSettings()
{
  $.ajax({
      type:"GET",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      url: 'settings',
  }).done(function(e, data) {
    // Special case for time
    e['time_hour'] = Math.floor(e.time / 60);
    e['time_minute']= e.time % 60;
    for(i in e) {
      $('#otherSettings').find('#' + i).val(e[i]);
    }
  }).fail(function(e, data) {
    alert('Unable to load settings, please reload');
  });

}

function updateBackend(thiz, value)
{
  j = jQuery(thiz);
  jj = j.parent();
  s = jj.data('sprinkler')
  if (s == null) {
    jj = jj.parent();
    s = jj.data('sprinkler')
    if (s == null) {
      jj = jj.parent();
      s = jj.data('sprinkler')
    }
  }
  i = thiz.id;
  v = (value == null ? j.val() : value); // Allow override

  if (!isNaN(parseInt(v)))
    v = parseInt(v);

  j.attr('disabled', 'disabled');
  req = {
    type:"POST",
    contentType: "application/json; charset=utf-8",
    dataType: "json"
  }

  var s1 = ['name', 'enable', 'open'];
  var s2 = ['duration', 'cycles', 'days', 'shift'];

  if (s1.includes(i)) {
    req.url = 'sprinkler/' + s.id;
    req.data = JSON.stringify( { [i] : v} );
  } else if (s2.includes(i)) {
    req.url = 'schedule/' + s.id;
    req.data = JSON.stringify( { [i] : v} );
  }
  $.ajax( req ).done(function(e, data){
    if (s2.includes(i)) {
      s.schedule = e;
      e = s;
    }
    setSprinkler(e, jj);
    j.removeAttr('disabled');
    updateProgramStatus();
  }).fail(function(e, data) {
    alert('Unable to update sprinklers, please reload!');
  });
}

function toggleEnable(thiz)
{
  j = jQuery(thiz);
  s = j.parent().parent().data('sprinkler')
  if (s.enabled) {
    j.removeClass('btn-success').addClass('btn-secondary');
    updateBackend(thiz, false);
  } else {
    j.removeClass('btn-secondary').addClass('btn-success');
    updateBackend(thiz, true);
  }
}

function showPIN(thiz)
{
  alert("PIN used by this valve: " + jQuery(thiz).parent().parent().data('sprinkler').pin );
}

function deleteStation(thiz)
{
  s = jQuery(thiz).parent().parent().data('sprinkler');
  if (confirm('Are you sure you wish to delete "' + s.name + '" (PIN ' + s.pin + ')')) {
    jQuery(thiz).parent().parent().remove();
    $.ajax({
      type:"POST",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      url: 'delete',
      data: JSON.stringify({ id: s.id })
    }).done(function(e, data){
      updateProgramStatus();
    }).fail(function(e, data) {
      alert('Unable to delete sprinkler station, please reload!');
    });
  }
}

function toggleManual(thiz)
{
  j = jQuery(thiz);
  s = j.parent().parent().data('sprinkler');
  if (s.open) {
    j.removeClass('btn-success').addClass('btn-primary').html('<svg class="bi bi-play" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10.804 8L5 4.633v6.734L10.804 8zm.792-.696a.802.802 0 010 1.392l-6.363 3.692C4.713 12.69 4 12.345 4 11.692V4.308c0-.653.713-.998 1.233-.696l6.363 3.692z" clip-rule="evenodd"/></svg>');
    updateBackend(thiz, false);
  } else {
    // First, remove any other ones
    $('#sprinklers #open').each(function() {
      $(this).removeClass('btn-success').addClass('btn-primary').html('<svg class="bi bi-play" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10.804 8L5 4.633v6.734L10.804 8zm.792-.696a.802.802 0 010 1.392l-6.363 3.692C4.713 12.69 4 12.345 4 11.692V4.308c0-.653.713-.998 1.233-.696l6.363 3.692z" clip-rule="evenodd"/></svg>');
      $(this).parent().parent().data('sprinkler').open = false;
    });
    j.removeClass('btn-primary').addClass('btn-success').html('<svg class="bi bi-stop" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3.5 5A1.5 1.5 0 015 3.5h6A1.5 1.5 0 0112.5 5v6a1.5 1.5 0 01-1.5 1.5H5A1.5 1.5 0 013.5 11V5zM5 4.5a.5.5 0 00-.5.5v6a.5.5 0 00.5.5h6a.5.5 0 00.5-.5V5a.5.5 0 00-.5-.5H5z" clip-rule="evenodd"/></svg>');
    updateBackend(thiz, true);
  }
}

function addSprinkler(sprinkler)
{
  var e = $('#template').clone().removeAttr('id').removeClass('d-none').attr('id', 'entry');
  setSprinkler(sprinkler, e);

  if (sprinkler.open) {
    e.find('#open').removeClass('btn-primary').addClass('btn-success').html('<svg class="bi bi-stop" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3.5 5A1.5 1.5 0 015 3.5h6A1.5 1.5 0 0112.5 5v6a1.5 1.5 0 01-1.5 1.5H5A1.5 1.5 0 013.5 11V5zM5 4.5a.5.5 0 00-.5.5v6a.5.5 0 00.5.5h6a.5.5 0 00.5-.5V5a.5.5 0 00-.5-.5H5z" clip-rule="evenodd"/></svg>');
  }

  e.find('#gpio').text(sprinkler.pin);

  e.find('#name').change(function() { updateBackend(this, null); });
  e.find('#duration').change(function() { updateBackend(this, null); });
  e.find('#cycles').change(function() { updateBackend(this, null); });
  e.find('#days').change(function() { updateBackend(this, null); });
  e.find('#shift').change(function() { updateBackend(this, null); });

  e.find('#enable').click(function() { toggleEnable(this); });
  e.find('#pin').click(function() { showPIN(this); });
  e.find('#delete').click(function() { deleteStation(this); });

  e.find('#open').click(function() { toggleManual(this); });

  e.appendTo('#sprinklers');
}

function setSprinkler(sprinkler, obj)
{
  obj.data('sprinkler', sprinkler);

  obj.find('#name').val(sprinkler.name);
  obj.find('#duration').val(sprinkler.schedule.duration);
  obj.find('#cycles').val(sprinkler.schedule.cycles);
  obj.find('#days').val(sprinkler.schedule.days);
  obj.find('#shift').val(sprinkler.schedule.shift);
  if (!sprinkler.enabled) {
    obj.find('#enable').removeClass('btn-success').addClass('btn-secondary');
  }
}

function updateProgramStatus() {
  $.ajax({
        type:"GET",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        url: 'program',
    }).done(function(e, data) {
      if (e.running)
        $('#programRunning').modal('show')
      // Update the runtime info
      if (e.duration > 0)
        $('#next-run').text('Next scheduled run happens at ' + time2str(e.start, false) + ' (runtime of ' + time2str(e.duration, true) + ')');
      else
        $('#next-run').text('No scheduled sprinklers today, next run in ' + e.next + ' day' + (e.next > 1 ? 's' : ''));
    }).fail(function(e, data) {
      alert('Unable to load program state, please reload');
    });
}

function time2str(m, units) {
  h = Math.floor(m / 60);
  m = Math.floor(m % 60);
  if (m < 10 && !units)
    m = '0' + m;
  if (units)
    return h + 'h' + m + 'm';
  return h + ':' + m;
}

function setup() {
  $('#add').click(function() {
    name = $('#add_name').val().trim()
    pin = $('#add_pin').val().trim();
    if (isNaN(parseInt(pin))) {
      alert('PIN has to be numeric');
      return;
    }
    pin = parseInt(pin);
    if (pin < 2) {
      alert('PIN cannot be lower than 2');
      return;
    }
    if (name.length == 0) {
      alert('Name cannot be empty');
      return;
    }

    // Make sure this isn't in use already
    var s = $('#sprinklers #entry');
    for(var i=0; i < s.length; i++){
      var element = s.eq(i);
      //do something with element
      if (element.data('sprinkler').pin == pin) {
        alert('PIN ' + pin + ' is already used by ' + element.data('sprinkler').name);
        return;
      }
    }
    // Let's add it
    $.ajax({
      type:"POST",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      url: 'add',
      data: JSON.stringify({
        'enabled' : true,
        'name' : name,
        'pin' : pin,
        'group' : 0,
        'schedule' : {
          duration: 1,
          cycles: 1,
          days: 1,
          shift: 0
        }
      })
    }).done(function(e, data){
      addSprinkler(e);
      $('#addSprinklerDialog').modal('hide');
      $('#add_name').val('');
      $('#add_pin').val('');
      updateProgramStatus();
    }).fail(function(e, data) {
      alert('Unable to add sprinkler station, please reload!');
    });
  });

  // Load settings
  loadSettings();
  $('#showSettings').click(function() {
    $('#otherSettings').modal('show');
  });
  $('#cancel').click(function() {
    $('#otherSettings').modal('hide');
    loadSettings();
  });
  $('#save').click(function() {
    data = {
      time : parseInt($('#time_hour').val())*60 + parseInt($('#time_minute').val()),
      timing : parseInt($('#timing').val()),
      scaling : parseInt($('#scaling').val())
    };

    $.ajax({
        type:"POST",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        url: 'settings',
        data: JSON.stringify(data),
    }).done(function(e, data) {
      $('#otherSettings').modal('hide');
      updateProgramStatus();
    }).fail(function(e, data) {
      alert('Unable to load settings, please reload');
    });
  });

  $.ajax({
    url:"/sprinklers",
    type:"GET",
  }).done(function(e, data){
    for (s in e) {
      s = e[s];
      addSprinkler(s);
    }
  }).fail(function(e, data) {
    alert('Unable to load sprinklers')
  });

  updateProgramStatus();

  $('#stopProgram').click(function() {
    if (confirm('Are you sure?')) {
      $.ajax({
            type:"POST",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            url: 'program',
            data: JSON.stringify({stop: true})
        }).done(function(e, data) {
          if (!e.running)
            $('#programRunning').modal('hide')
        }).fail(function(e, data) {
          alert('Unable to load program state, please reload');
        });
    }
  });

  $('#runProgram').click(function() {
    if (confirm('Are you sure?')) {
      $.ajax({
            type:"POST",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            url: 'program',
            data: JSON.stringify({start: true})
        }).done(function(e, data) {
          if (e.running)
            $('#programRunning').modal('show')
        }).fail(function(e, data) {
          alert('Unable to get program state, please reload');
        });
    }
  });
}

