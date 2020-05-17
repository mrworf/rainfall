function addSprinkler(sprinkler)
{
  var e = $('#template').clone().removeAttr('id').removeClass('d-none');
  e.data(sprinkler);
  e.find('#name').val(sprinkler.name);
  e.find('#duration').val(sprinkler.schedule.duration);
  e.find('#cycles').val(sprinkler.schedule.cycles);
  e.find('#days').val(sprinkler.schedule.days);
  e.find('#shift').val(sprinkler.schedule.shift);
  e.appendTo('#sprinklers');
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

