from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import OperatingDataSerializer

@api_view(['POST'])
def receive_operating_data(request):
    if request.method == 'POST':
        serializer = OperatingDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)