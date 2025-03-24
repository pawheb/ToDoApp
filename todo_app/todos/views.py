from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import ToDo, Group
from .serializers import ToDoSerializer, UserSerializer, GroupSerializer

# Rejestracja użytkownika
class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()  # Używamy niestandardowego modelu użytkownika
    serializer_class = UserSerializer

# Login – token JWT
class LoginView(APIView):
    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid Credentials'}, status=400)

# Listowanie i tworzenie zadań
class ToDoListCreateView(generics.ListCreateAPIView):
    serializer_class = ToDoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ToDo.objects.all()  # Admin może zobaczyć wszystkie zadania
        return ToDo.objects.filter(user=self.request.user)  # Inni użytkownicy tylko swoje

    def perform_create(self, serializer):
        group_id = self.request.data.get('group')
        user_id = self.request.data.get('user')
        
        if group_id:
            group_instance = Group.objects.get(id=group_id)
            for member in group_instance.members.all():
                serializer.save(user=member)
        elif user_id:
            user_instance = get_user_model().objects.get(id=user_id)  # Używamy get_user_model()
            serializer.save(user=user_instance)
        else:
            # Domyślnie przypisz zadanie do aktualnie zalogowanego użytkownika
            serializer.save(user=self.request.user)

# Widok szczegółów zadania – umożliwia aktualizację i usunięcie zadania
class ToDoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ToDoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ToDo.objects.all()  # Admin może zobaczyć wszystkie zadania
        return ToDo.objects.filter(user=self.request.user)  # Inni użytkownicy tylko swoje

# CRUD dla grupy
class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

# Admin: dodaje zadanie użytkownikowi lub grupie
class AdminAssignToDoView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        data = request.data
        group_id = data.get('group')
        user_id = data.get('user')
        serializer = ToDoSerializer(data=data)

        if serializer.is_valid():
            if group_id:
                group = Group.objects.get(id=group_id)
                for member in group.members.all():
                    ToDo.objects.create(
                        user=member,
                        group=group,
                        title=data['title'],
                        description=data.get('description', ''),
                        priority=data.get('priority', 'Medium'),
                        due_date=data.get('due_date', None)
                    )
                return Response({'message': 'Zadania dodane grupie.'})
            elif user_id:
                serializer.save(user=get_user_model().objects.get(id=user_id))  # Używamy get_user_model()
                return Response(serializer.data)
            else:
                return Response({'error': 'Podaj group_id lub user_id.'}, status=400)
        return Response(serializer.errors, status=400)
