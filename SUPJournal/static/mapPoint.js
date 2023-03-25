var userPoint = null

/*
Показывает точку с заданными координатами,
если данная точка не отображается на карте а координаты переданы то создается точка и показывается.
В случае если точка создана но в координаты передается null точка убирается с карты.
Если точка уже есть и передаются новые координаты точка перемещается.
*/
function showUserPoint (coord) {
  if (userPoint == null && coord != null) {
    userPoint = L.marker(coord).addTo(map_TrainingMap)
  } else if (coord == null && userPoint != null) {
    userPoint.remove()
    userPoint = null
  } else if (coord != null && userPoint != null) {
    userPoint.setLatLng(coord).move()
  }
}