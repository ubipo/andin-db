[out:json][timeout:25];
(
  way["indoor"="room"]({{bbox}});
)->.rooms;
.rooms > ->.nodes;
.nodes < ->.all;
.all out meta;
.all > ->.nodes;
.nodes out skel qt;
