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
    req.url = '/sprinkler/' + s.id;
    req.data = JSON.stringify( { [i] : v} );
  } else if (s2.includes(i)) {
    req.url = '/schedule/' + s.id;
    req.data = JSON.stringify( { [i] : v} );
  }
  $.ajax( req ).done(function(e, data){
    if (s2.includes(i)) {
      s.schedule = e;
      e = s;
    }
    setSprinkler(e, jj);
    j.removeAttr('disabled');
  }).fail(function(e, data) {
    alert('Unable to update sprinklers, please reload!');
  });
}

function toggleEnable(thiz)
{
  j = jQuery(thiz);
  s = j.parent().parent().parent().data('sprinkler')
  if (s.enabled) {
    j.text('Enable');
    updateBackend(thiz, false);
  } else {
    j.text('Disable');
    updateBackend(thiz, true);
  }
}

function showPIN(thiz)
{
  alert("PIN used by this valve: " + jQuery(thiz).parent().parent().parent().data('sprinkler').pin );
}

function deleteStation(thiz)
{
  s = jQuery(thiz).parent().parent().parent().data('sprinkler');
  if (confirm('Are you sure you wish to delete "' + s.name + '" (PIN ' + s.pin + ')')) {
    jQuery(thiz).parent().parent().parent().remove();
    $.ajax({
      type:"POST",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      url: '/delete',
      data: JSON.stringify({ id: s.id })
    }).done(function(e, data){
      ;
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
    j.removeClass('btn-success').addClass('btn-primary').text('Manual');
    updateBackend(thiz, false);
  } else {
    // First, remove any other ones
    $('#sprinklers #open').each(function() {
      $(this).removeClass('btn-success').addClass('btn-primary').text('Manual');
      $(this).parent().parent().data('sprinkler').open = false;
    });
    j.removeClass('btn-primary').addClass('btn-success').text('Stop');
    updateBackend(thiz, true);
  }
}

function addSprinkler(sprinkler)
{
  var e = $('#template').clone().removeAttr('id').removeClass('d-none').attr('id', 'entry');
  setSprinkler(sprinkler, e);

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
      url: '/add',
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

    }).fail(function(e, data) {
      alert('Unable to add sprinkler station, please reload!');
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
}

