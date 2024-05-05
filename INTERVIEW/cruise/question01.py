"""
For each ride data, the first is the name of the ride, second is the ride costs, third is the ride rating
"""

ride_data = [('spiderman', 3.25, 5),
             ('hulk', 4.50, 4),
             ('superman', 5.75, 4),
             ('superman', 6.25, 3),
             ('ironman', 4.00, 5),
             ('hulk', 5.50, 3),
             ('spiderman', 3.75, 5),
             ]


class ride_share:
    def __init__(self, ride_data):
        self.ride_data = ride_data

    def find_ride_num(self, ride_name: str) -> int:
        ride_num = 0
        for ride in self.ride_data:
            if ride[0] == ride_name:
                ride_num += 1
        return ride_num

    def find_avg_rating(self, ride_name: str) -> float:
        ride_rating = []
        for ride in self.ride_data:
            if ride[0] == ride_name:
                ride_rating.append(ride[2])
        return round(sum(ride_rating) / len(ride_rating), 2)


if __name__ == '__main__':
    ride = ride_share(ride_data)
    print(f'{ride.find_ride_num("hulk") = }')
    print(f'{ride.find_avg_rating("hulk") = }')
