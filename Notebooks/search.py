from query_optimisation import extract_query, search_with_filter


def search(query, limit=10):
    food, meal, rank = extract_query(query)
    result = search_with_filter(query = query,meal_type = meal,food_type = food, limit = limit * 5)
    points = result.points
    if rank:
        field, descend = rank
        points = sorted(points, key = lambda p:p.payload[field], reverse = descend
                       )
    return points[:limit]


