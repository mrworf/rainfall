function getInfo(method, onResult) {
  $.ajax("cmd.php?method=" + method)
  .done(onResult);
}
function showPanel() {
  $("#msg").show();
  for (i = 0; i != 11; i++) {
    $("#sprinkler" + i).show();
  }
  $("#override").show();
  $("#wait").remove();
}

function checkManual() {
  $.ajax("cmd.php?method=station").done(function(data) {
    runner = -1;
    for (i = 0; i != 11; ++i) {
      if (data.result[i] != 0) {
        runner = i;
        break;
      }
    }

    // Coolness, if program is running, BLOCK ALL!
    if (data.result[11] != 0) {
      runner = 11;
    }

    for (i = 0; i != 11; ++i) {
      if (runner == i) {
        $("#override" + i).attr("disabled", false);
        $("#override" + i).text("Stop");
      } else {
        $("#override" + i).attr("disabled", runner != -1);
        $("#override" + i).text("Manual");
      }
    }

    if (runner == 11) {
      $("#override").attr("disabled", true);
      $("#override").css("color", "white");
      $("#override").text("Sprinkler Program Running");
    } else {
      $("#override").attr("disabled", false);
      $("#override").css("color", "black");
      $("#override").text("Start sprinkler program now");
    }

    if (runner != -1)
      setTimeout(function() {checkManual();}, 30000);
  });
}

function checkStatus() {
  $.ajax("cmd.php?method=operation").done(function(data) {
    if (data.result.runreason != 0) {
      switch (data.result.runreason) {
        case 1:
          msg = "Sprinkler program running now, according to schedule";
          break;
        case 3:
          msg = "Sprinkler program running now, according to schedule with extra water due to heat";
          break;
        case 5:
        case 6:
        case 7:
        case 4:
          msg = "Sprinkler program manually started";
          if ($("#override").css("background-color") == "rgb(255, 0, 0)")
            $("#override").css("background-color", "rgb(100, 100, 255)");
          else
            $("#override").css("background-color", "rgb(255, 0, 0)");
          break;
        default:
          msg = "Sprinkler program running now";
      }
    } else if (data.result.delayreason && data.result.manual == 0) {
      var m = Math.round((data.result.delaystart + 129600 - Date.now()/1000) / 60 % 60);
      var h = Math.round((data.result.delaystart + 129600 - Date.now()/1000) / 3600);
      msg = "Sprinklers delayed 36hrs (" + h + "h " + m + "m remaining) due to ";
      if ((data.result.delayreason & 3) == 3)
        msg += "rain and cold weather (below 40&deg;F at night or 72&deg;F at day)";
      else if (data.result.delayreason & 2)
        msg += "rain";
      else if (data.result.delayreason & 1)
        msg += "cold weather (below 40&deg;F at night or 72&deg;F at day)";
    } else if (data.result.manual != 0) {
      msg = "Sprinkler program started manually";
    } else if (data.result.additional == 2) {
      msg = "Sprinklers running with increased amount of water due to heatwave (80&deg;F+ for more than two days)";
    } else {
      msg = "Sprinklers running as expected";
    }
    $("#msg").html(msg);
    //checkInit();
  });
}

function assignMethod(type, element, func) {
  for (i = 0; i != 11; ++i) {
    $("#" + element + i).on(type, {sprinkler: i}, func);
  }
}

$(
function() {
  getInfo("status", function(obj) {
    result = obj.result;
    for (i = 0; i != 11; ++i) {
      $("#toggle" + i).text(result[i] ? "Enabled" : "Disabled");
      $("#toggle" + i).css("background-color", result[i] ? "#00ff00" : "#ff0000");
    }
    getInfo("runtime", function(obj) {
      result = obj.result;
      for (i = 0; i != 11; ++i) {
        $("#runtime" + i).val(result[i]);
      }
      getInfo("cycles", function(obj) {
        result = obj.result;
        for (i = 0; i != 11; ++i) {
          $("#cycles" + i).val(result[i]);
        }
        getInfo("stepping", function(obj) {
          result = obj.result;
          for (i = 0; i != 11; ++i) {
            $("#stepping" + i).val(result[i]);
          }
          showPanel();
          checkManual();

          // Lastly, grab latest status from the system
          checkStatus();
          setInterval(function() { checkStatus(); }, 10000);
        });
      });
    });
  });

  // Assign functionality to all buttons/boxes
  assignMethod("click", "toggle", function(obj) {
    $("#toggle" + obj.data.sprinkler).attr("disabled", true);
    value = obj.currentTarget.textContent == "Disabled" ? 0 : 1;
    $.ajax("cmd.php?method=status&set=" + obj.data.sprinkler + "&value=" + value)
    .done(function() {
      obj.currentTarget.textContent = value ? "Disabled" : "Enabled";
      $("#toggle" + obj.data.sprinkler).attr("disabled", false);
      $("#toggle" + obj.data.sprinkler).css("background-color", value ? "#ff0000" : "#00ff00");
    });
  });
  assignMethod("change", "runtime", function(obj) {
    $("#runtime" + obj.data.sprinkler).attr("disabled", true);
    $.ajax("cmd.php?method=runtime&set=" + obj.data.sprinkler + "&value=" + obj.currentTarget.value)
    .done(function() {
      $("#runtime" + obj.data.sprinkler).attr("disabled", false);
    });
  });
  assignMethod("change", "cycles", function(obj) {
    $("#cycles" + obj.data.sprinkler).attr("disabled", true);
    $.ajax("cmd.php?method=cycles&set=" + obj.data.sprinkler + "&value=" + obj.currentTarget.value)
    .done(function() {
      $("#cycles" + obj.data.sprinkler).attr("disabled", false);
    });
  });
  assignMethod("change", "stepping", function(obj) {
    $("#stepping" + obj.data.sprinkler).attr("disabled", true);
    $.ajax("cmd.php?method=stepping&set=" + obj.data.sprinkler + "&value=" + obj.currentTarget.value)
    .done(function() {
      $("#stepping" + obj.data.sprinkler).attr("disabled", false);
    });
  });
  assignMethod("click", "override", function(obj) {
    $("#override" + obj.data.sprinkler).attr("disabled", true);
    if (obj.currentTarget.textContent == "Stop") {
      if (confirm("This will turn off the station. Continue?")) {
        $.ajax("cmd.php?method=override&set=" + obj.data.sprinkler + "&value=" + 0)
        .done(function() {
          checkManual();
        });
      } else {
        $("#override" + obj.data.sprinkler).attr("disabled", false);
      }
    } else {
      if (confirm("This will cause this sprinkler to run for 15min and cannot be interrupted.\n\nAre you sure?")) {
        $.ajax("cmd.php?method=override&set=" + obj.data.sprinkler + "&value=" + 1)
        .done(function() {
          checkManual();
        });
      } else {
        $("#override" + obj.data.sprinkler).attr("disabled", false);
      }
    }
  });

  $("#override").click(function() {
    $("#override").attr("disabled", true);
    if (confirm("Are you absolutely sure?\n\nThis will force the sprinkler system to run it's program with any and all stations and with the durations and cycles. This cannot be aborted.\n\nARE YOU SURE?")) {
      $.ajax("cmd.php?method=overrideprogram").done(function() {
        $("#override").attr("disabled", false);
        checkManual();
      });
    } else {
      $("#override").attr("disabled", false);
    }
  })
}
);
