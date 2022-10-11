from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from .models import *

# Create your views here.
@api_view(["GET"])
def listOfViolators(request, *args, **kwargs):
    violators = Violator.objects.all()
    if violators:
        data = ViolatorSerializer(violators, many=True).data
        return Response(data)
    return Response({'message': 'violators is none'})