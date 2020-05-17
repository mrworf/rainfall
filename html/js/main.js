function updateBackend(thiz, value)
{
  j = jQuery(thiz);
  jj = j.parent();
  s = jj.data('sprinkler')
  if (s == null) {
    jj = jj.parent().parent();
    s = jj.data('sprinkler')
  }
  i = thiz.id;
  v = (value == null ? j.val() : value); // Allow override
  console.log('Sprinkler: ' + s.id + ' Field: ' + i + ', value: ' + v);
  j.attr('disabled', 'disabled');
  req = {
    type:"POST",
    contentType: "application/json; charset=utf-8",
    dataType: "json"
  }

  var s1 = ['name', 'enabled'];
  var s2 = ['duration', 'cycles', 'days', 'shift'];

  if (s1.includes(i)) {
    req.url = '/sprinkler/' + s.id;
    req.data = JSON.stringify( { [i] : v} );
  } else if (s2.includes(i)) {
    req.url = '/schedule/' + s.id;
    req.data = JSON.stringify( { [i] : parseInt(v)} );
  }
  $.ajax( req ).done(function(e, data){
    console.log(e);
    if (s2.includes(i)) {
      s.schedule = e;
      e = s;
    }
    jj.data('sprinkler', e);
    setSprinkler(e, jj);
    j.removeAttr('disabled');
  }).fail(function(e, data) {
    console.log(data);
    alert('Unable to update sprinklers, please reload!\n\n' + data);
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
  }
}

function addSprinkler(sprinkler)
{
  var e = $('#template').clone().removeAttr('id').removeClass('d-none');
  setSprinkler(sprinkler, e);

  e.find('#name').change(function() { updateBackend(this, null); });
  e.find('#duration').change(function() { updateBackend(this, null); });
  e.find('#cycles').change(function() { updateBackend(this, null); });
  e.find('#days').change(function() { updateBackend(this, null); });
  e.find('#shift').change(function() { updateBackend(this, null); });

  e.find('#enable').click(function() { toggleEnable(this); })
  e.find('#pin').click(function() { showPIN(this); })
  e.find('#delete').click(function() { deleteStation(this); })

  e.appendTo('#sprinklers');
}

function setSprinkler(sprinkler, obj)
{
  console.log(sprinkler);
  obj.data('sprinkler', sprinkler);

  obj.find('#name').val(sprinkler.name);
  obj.find('#duration').val(sprinkler.schedule.duration);
  obj.find('#cycles').val(sprinkler.schedule.cycles);
  obj.find('#days').val(sprinkler.schedule.days);
  obj.find('#shift').val(sprinkler.schedule.shift);
}

function setup() {
  html = "";
  $.ajax({
    url:"/sprinklers",
    type:"GET",
  }).done(function(e, data){
    for (s in e) {
      s = e[s];
      //console.log(s);
      addSprinkler(s);
    }
  }).fail(function(e, data) {
    alert('Unable to load sprinklers')
  });
}

