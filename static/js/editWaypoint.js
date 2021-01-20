const MAPBOX_API_KEY = "pk.eyJ1Ijoicnlhbml0byIsImEiOiJjazM2NGZtbmIwZTJuM2Nxanpsa2tlOWR5In0.EmeKG8ONjjFsgwaE5KSH7A";

$(function() {

  $.getJSON('/api/locations', function(data) {

    var map = L.map('map',
    {
      fullscreenControl: true,
      minZoom: 5
    }).setView([51.584054476437316, -2.9993104934692387], 15);

    var basemaps = [
      L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' + MAPBOX_API_KEY, {
        maxZoom: 19,
      	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
      		'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      		'Imagery &copy; <a href="https://www.mapbox.com/">Mapbox</a>',
      	id: 'mapbox.streets'
      }),
      L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/tiles/256/{z}/{x}/{y}?access_token=' + MAPBOX_API_KEY, {
        maxZoom: 19,
      	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
      		'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      		'Imagery &copy; <a href="https://www.mapbox.com/">Mapbox</a>',
      	id: 'mapbox.satellite'
      })
    ];

    map.addControl(L.control.basemaps({
      basemaps: basemaps,
      tileX: 32222,  // tile X coordinate
      tileY: 21769,  // tile Y coordinate
      tileZ: 16   // tile zoom level
    }));

    var marker;
    // Add latitude and longitude to the form inputs on click
    map.on('click', function(e){

      if(allow_selecting == true) {

        if (marker) {
          map.removeLayer(marker);
        }

        var coord = e.latlng;
        var lat = coord.lat;
        var lng = coord.lng;
        $('#latitude').val(lat);
        $('#longitude').val(lng);

        // Code adapted from https://github.com/pointhi/leaflet-color-markers
        marker = L.marker([lat, lng]).addTo(map);

        $("#map").removeClass("crosshair");
        allow_selecting = false;

      }

    });

    let routes = [];
    data.forEach(function(row) {
      if (routes.includes(row['route']) == false) {
        routes.push(row['route']);
      }
    });

    for (j = 1; j <= routes.length; j++) {

      let name, color, icon_html;
      if (j == 1) {
        name = 'Easy Route';
        color = '#007bff';
        icon_html = '<span class="star"></span>';
      } else if (j == 2) {
        name = 'Hard Route';
        color = 'red';
        icon_html = '<span class="star red"></span>';
      }

      // Salesman.js - https://github.com/lovasoa/salesman.js
      // Calculates the easiest route between all points on the map
      let points = []
      data.forEach(function(row) {
        if (row['route'] == j) {
          points.push(new Point(row['latitude'], row['longitude']));
        }
      });

      var solution = solve(points, 0.999999);
      var ordered_points = solution.map(i => points[i]);

      let waypoints = []
      ordered_points.forEach(function(point) {
          waypoints.push(L.latLng(point['x'], point['y']));
      });

      if(waypoints.length > 0) {

        // Loop back around to start of route
        waypoints.push(waypoints[0]);

        // Required to overcome the 25 co-ordinate limit per route
        let mapbox_limit = 24;
        let number_of_loops = Math.ceil((waypoints.length+1)/mapbox_limit);

        for (var i = 0; i < number_of_loops; i++) {

          let minimum, maximum;

          minimum = i * mapbox_limit;
          maximum = ((i+1) * mapbox_limit) + 1;

          let current_waypoints = waypoints.slice(minimum, maximum);

          L.Routing.control({
            waypoints: current_waypoints,
            draggableWaypoints: false,
            addWaypoints: false,
            fitSelectedRoutes: false,
            summaryTemplate: '<h2><span class="star" style="background:' + color + ';"></span> ' + name + '</h2><h3>{distance}, {time}</h3>',
            lineOptions: {
              styles: [{color: color, opacity: .5, weight: 6}]
            },
            createMarker: function(i, wp, n) {
      				return L.marker(wp.latLng, {
      					icon: L.divIcon({
                  html: icon_html
                })
      				}).on('click', function(e) {

                // Remove selected location on waypoint click
                if (marker) {
                  map.removeLayer(marker);
                }

                $.getJSON('/api/location/'+e.latlng['lat']+'/'+e.latlng['lng'], function(location) {

                  $("input, textarea, form button").prop("disabled", false);

                  $('.outlined').removeClass('outlined');

                  // Toggle outline code adapted from https://stackoverflow.com/a/53416108
                  e.originalEvent.target.closest(".leaflet-interactive").classList.toggle("outlined");

                  $("#" + location['route']).prop("checked", true);
                  $('#id').val(location['id']);
                  $('#latitude').val(location['latitude']);
                  $('#longitude').val(location['longitude']);
                  $('#name').val(location['name'] ? location['name'] : "");
                  $('#description').val(location['description'] ? location['description'] : "");
                  $('#welsh-name').val(location['welsh_name'] ? location['welsh_name'] : "");
                  $('#welsh-description').val(location['welsh_description'] ? location['welsh_description'] : "");
                  $('.custom-file-label').html(location['image'] ? location['image'].split('/').pop() : "Choose file...");

                });

              });
      			},
            router: L.Routing.mapbox(MAPBOX_API_KEY,
              {
                profile: 'mapbox/walking'
              })
            }
          ).addTo(map);

        }

      }

    }

  });

  var allow_selecting = false;

  $("#select-location").click(function() {
    if (allow_selecting == false) {
      allow_selecting = true;
      $("#map").addClass("crosshair");
    }
  });

  // Code adapted from https://stackoverflow.com/a/51497456
  $('input[type="file"]').change(function(e){
     var fileName = e.target.files[0].name;
     $('.custom-file-label').html(fileName);

     $('#remove-image').val("");
   });

   $('#remove-btn').click(function() {
     $('.custom-file-label').html("Choose file...");
     $('#remove-image').val(true);
   });

});
