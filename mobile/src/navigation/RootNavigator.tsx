import React, { useEffect } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuthStore } from '../store/authStore';

// Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import DashboardScreen from '../screens/DashboardScreen';
import PapersScreen from '../screens/PapersScreen';
import AnalysisScreen from '../screens/AnalysisScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#0ea5e9',
        },
        headerTintColor: '#fff',
        tabBarActiveTintColor: '#0ea5e9',
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{ title: '대시보드' }}
      />
      <Tab.Screen
        name="Papers"
        component={PapersScreen}
        options={{ title: '논문' }}
      />
      <Tab.Screen
        name="Analysis"
        component={AnalysisScreen}
        options={{ title: 'AI 분석' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: '프로필' }}
      />
    </Tab.Navigator>
  );
}

export default function RootNavigator() {
  const { isAuthenticated, loadAuth } = useAuthStore();

  useEffect(() => {
    loadAuth();
  }, []);

  return isAuthenticated ? <MainTabs /> : <AuthStack />;
}
