# API

## [GET] /sprinklers

Returns a JSON with all sprinklers as an array of a map

```
[
  {
    'id' : <int: sprinkler id>,
    'name' : <string: sprinkler name>,
    'enabled' : <boolean: sprinkler enabled in program>,
    'open' : <boolean: sprinkler's valve open>,
    'pin' : <int: GPIO pin on Raspberry Pi>,
    'group' : <int: Not used yet>,
    'schedule' : {
      'duration' : <int: minutes>,
      'cycles' : <int: cycles it should run, minium 1>,
      'days' : <int: days it should run>,
      'shift' : <int: shift start day>
    }
  },
  ...
]
```

## [GET] /sprinkler/<int: sprinkler id>

Returns a single sprinkler as defined in the id. Return is the same as `/sprinklers` but only returns a single sprinkler without the array wrapping.

## [POST] /sprinkler/<int: sprinkler id>

Allows setting properties and controlling the sprinkler. You send a JSON with one or more of the following fields:

```
{
  'open' : <boolean: open the valve>,
  'name' : <string: change the name of the sprinkler>,
  'enable' : <boolean: enable the sprinkler in the program>,
  'group' : <int: set the group this sprinkler belongs to (UNUSED)>
}
```

This request will return the sprinkler in the same was as `/sprinkler/<int: sprinkler id>`

## [GET] /schedule/<int: sprinkler id>

Returns the schedule for specific sprinkler

```
{
  'duration' : <int: minutes>,
  'cycles' : <int: cycles it should run, minium 1>,
  'days' : <int: days it should run>,
  'shift' : <int: shift start day>
}
```

## [POST] /schedule/<int: sprinkler id>

Allows changing of the schedule, takes the same format as returned by the GET call. You can omitt fields which will not change.

```
{
  'duration' : <int: minutes>,
  'cycles' : <int: cycles it should run, minium 1>,
  'days' : <int: days it should run>,
  'shift' : <int: shift start day>
}
```

## [POST] /add

Adds a new sprinkler to the system.

```
{
  'name' : <string: sprinkler name>,
  'open' : <boolean: sprinkler's valve open>,
  'pin' : <int: GPIO pin on Raspberry Pi>,
  'group' : <int: Not used yet>,
  'schedule' : {
    'duration' : <int: minutes>,
    'cycles' : <int: cycles it should run, minium 1>,
    'days' : <int: days it should run>,
    'shift' : <int: shift start day>
  }
}
```

All fields are required to create a sprinkler. Once created, returns the same output as `/sprinkler/<int: sprinkler id>` with the benefit that you know get the `id` of the newly created sprinkler.

## [POST] /delete

Deletes an existing sprinkler. Takes a JSON map with only one entry

```
{
  'id' : <int: sprinkler id>
}
```

If successful, returns

```
{
  'deleted' : <int: sprinkler id>
}
```

If the sprinkler doesn't exist or the `id` is missing, this call returns HTTP 404

## [GET] /program

Returns the state of the program. Currently only tells if the program is running or not.

```
{
  'running' : <boolean: true if running>
}
```

## [POST] /program

Controls the program feature. Currently allows start/stop.

```
{
  'stop' : <boolean: true if program should stop>,
  'start' : <boolean: true if program should start>
}
```

If stop is found, then that takes priority over start.

Returns status of program after call

```
{
  'running' : <boolean: true if running>
}
```

## [GET] /settings

Returns current global settings

```
{
  'time' : <int: military time of when program should run>,
  'timing' : <int: 0 = Finish by 'time', 1 = Start at 'time'>
}
```

## [POST] /settings

Alters the global settings

```
{
  'time' : <int: military time of when program should run>,
  'timing' : <int: 0 = Finish by 'time', 1 = Start at 'time'>
}
```

Returns the new settings as a result if successful.
