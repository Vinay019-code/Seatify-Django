from django.shortcuts import render,get_object_or_404,redirect
from.models import Movie,Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

def home(request):
    search = request.GET.get('search')
    # movies = Movie.objects.filter(is_upcoming=False)
    category = request.GET.get('category')

    movies=Movie.objects.all()
    total_movies = Movie.objects.count()
    context = {
    'movies': movies,
    'total_movies': total_movies,
}
    
    if search:
        movies = movies.filter(
            title__icontains=search
        )
    if category:
        movies = movies.filter(
        category=category
    )


    return render(
        request, 
        'movies/movie_list.html',
        {'movies': movies}
        )
def movie_detail(request, id):

    movie = get_object_or_404(
        Movie,
        id=id
    )

    reviews = Review.objects.filter(
        movie=movie
    ).order_by('-created_at')

    if request.method == "POST":

        if request.user.is_authenticated:

            form = ReviewForm(request.POST)

            if form.is_valid():
                already_reviewed = Review.objects.filter(
                    movie=movie,
                    user=request.user
                    ).exists()
                if not already_reviewed:
                    review = form.save(
                        commit=False
                 )
                    review.movie = movie
                    review.user = request.user
                    review.save()

                return redirect(
                    'movie_detail',
                    id=movie.id
                )

    else:

        form = ReviewForm()

    average_rating = reviews.aggregate(
    Avg('rating')
)['rating__avg']

    return render(
        request,
        'movies/movie_detail.html',
        {
            'movie': movie,
            'reviews': reviews,
            'form': form,
            'average_rating': average_rating
        }
    )
