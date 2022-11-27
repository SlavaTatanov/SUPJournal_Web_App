class Workout:
	def __init__(self, duration, date, time="00.00"):
		self.duration = round(duration/60, 4)
		self.date = date
		self.time = time


class DistanceWorkout(Workout):
	def __init__(self, duration, date, distance, time="00.00"):
		super().__init__(duration, date, time)
		self.distance = distance
		self.speed = round(self.distance/self.duration, 1)


class WaterSport(DistanceWorkout):

	def __init__(self, duration, date, distance, time="00:00"):
		super().__init__(duration, date, distance, time)
		self.knots = self.to_knots()
		self.nautical_miles = self.to_nautical_mile()
			
	def to_knots(self):
		"""Вычисляет скорость в узлах"""
		return round(self.speed * 0.54, 1)
						
	def to_nautical_mile(self):
		"""Вычисляет морские мили"""
		return round(self.distance * 0.54, 2)
		
		
one = WaterSport(78, "2022-11-17", 5.5)
print(str(one.knots) + " узлов")
print(str(one.nautical_miles) + " морских миль")
	
	