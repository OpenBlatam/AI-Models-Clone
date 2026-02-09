import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Modal,
  Alert,
  Switch,
  FlatList,
  Image,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';
import { validateFormData } from '../../lib/validation/validation-schemas';
import { secureStorage } from '../../lib/security/secure-storage';
import { AccessibleButton } from '../accessibility/accessible-button';
import { ErrorBoundary } from '../error-boundary/error-boundary';

interface TestableComponentProps {
  onNavigate?: (screen: string) => void;
  onShowModal?: (modalType: string) => void;
}

interface ListItem {
  id: number;
  title: string;
  description: string;
  imageUrl?: string;
}

const { width: screenWidth } = Dimensions.get('window');

export function DetoxTestableComponents({ onNavigate, onShowModal }: TestableComponentProps) {
  const { t } = useI18n();
  const { theme, user, notifications } = useAppStore();
  const { trackRender, trackInteraction } = useOptimizedPerformance();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [modalDescription, setModalDescription] = useState('');
  const [isSwitchOn, setIsSwitchOn] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState(0);
  const [showSearch, setShowSearch] = useState(false);
  const [showDrawer, setShowDrawer] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('home');
  const [listItems, setListItems] = useState<ListItem[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // Track component renders for performance testing
  trackRender('DetoxTestableComponents');

  // Mock data for list items
  const mockListItems: ListItem[] = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    title: `Item ${i + 1}`,
    description: `Description for item ${i + 1}`,
    imageUrl: `https://picsum.photos/200/200?random=${i}`,
  }));

  const handleLogin = useCallback(async () => {
    trackInteraction('login_attempt');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validate form data
      const formData = { email, password };
      const validation = validateFormData('login', formData);
      
      if (!validation.success) {
        // Show validation errors
        return;
      }
      
      // Simulate successful login
      onNavigate?.('home');
    } catch (error) {
      // Handle login error
    } finally {
      setIsLoading(false);
    }
  }, [email, password, onNavigate, trackInteraction]);

  const handleRegister = useCallback(async () => {
    trackInteraction('register_attempt');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validate form data
      const formData = { name, email, password, confirmPassword };
      const validation = validateFormData('register', formData);
      
      if (!validation.success) {
        // Show validation errors
        return;
      }
      
      // Simulate successful registration
      onNavigate?.('home');
    } catch (error) {
      // Handle registration error
    } finally {
      setIsLoading(false);
    }
  }, [name, email, password, confirmPassword, onNavigate, trackInteraction]);

  const handleLogout = useCallback(async () => {
    trackInteraction('logout_attempt');
    
    Alert.alert(
      'Confirm Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await secureStorage.removeItem('authToken');
              onNavigate?.('login');
            } catch (error) {
              // Handle logout error
            }
          },
        },
      ]
    );
  }, [onNavigate, trackInteraction]);

  const handleSaveSettings = useCallback(async () => {
    trackInteraction('save_settings');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Save API key securely
      await secureStorage.setItem('apiKey', apiKey);
      
      // Show success message
    } catch (error) {
      // Handle save error
    } finally {
      setIsLoading(false);
    }
  }, [apiKey, trackInteraction]);

  const handleSearch = useCallback(() => {
    trackInteraction('search_performed');
    setShowSearch(true);
  }, [trackInteraction]);

  const handleApplyFilter = useCallback(() => {
    trackInteraction('filter_applied');
    setShowSearch(false);
  }, [trackInteraction]);

  const handlePullToRefresh = useCallback(async () => {
    trackInteraction('pull_to_refresh');
    setRefreshing(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setListItems(mockListItems);
    } catch (error) {
      // Handle refresh error
    } finally {
      setRefreshing(false);
    }
  }, [trackInteraction]);

  const handleListItemPress = useCallback((item: ListItem) => {
    trackInteraction('list_item_pressed');
    onNavigate?.('detail');
  }, [onNavigate, trackInteraction]);

  const handleSwipeAction = useCallback((item: ListItem) => {
    trackInteraction('swipe_action');
    // Handle swipe action
  }, [trackInteraction]);

  const handleLongPress = useCallback((item: ListItem) => {
    trackInteraction('long_press');
    // Show context menu
  }, [trackInteraction]);

  const handleModalSave = useCallback(async () => {
    trackInteraction('modal_save');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setIsModalVisible(false);
      setModalTitle('');
      setModalDescription('');
    } catch (error) {
      // Handle save error
    } finally {
      setIsLoading(false);
    }
  }, [trackInteraction]);

  const handleBiometricLogin = useCallback(async () => {
    trackInteraction('biometric_login');
    try {
      // Simulate biometric authentication
      await new Promise(resolve => setTimeout(resolve, 500));
      onNavigate?.('home');
    } catch (error) {
      // Handle biometric error
    }
  }, [onNavigate, trackInteraction]);

  const renderListItem = useCallback(({ item }: { item: ListItem }) => (
    <TouchableOpacity
      testID={`home-list-item-${item.id}`}
      onPress={() => handleListItemPress(item)}
      onLongPress={() => handleLongPress(item)}
      style={{
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.border,
        flexDirection: 'row',
        alignItems: 'center',
      }}
    >
      {item.imageUrl && (
        <Image
          testID={`item-image-${item.id}`}
          source={{ uri: item.imageUrl }}
          style={{ width: 50, height: 50, borderRadius: 25, marginRight: 12 }}
          resizeMode="cover"
        />
      )}
      <View style={{ flex: 1 }}>
        <Text style={{ fontSize: 16, fontWeight: 'bold', color: theme.colors.text }}>
          {item.title}
        </Text>
        <Text style={{ fontSize: 14, color: theme.colors.textSecondary }}>
          {item.description}
        </Text>
      </View>
    </TouchableOpacity>
  ), [theme.colors, handleListItemPress, handleLongPress]);

  const renderLoginScreen = () => (
    <View testID="login-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('login.title')}
      </Text>
      
      <TextInput
        testID="email-input"
        placeholder={t('login.email')}
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="password-input"
        placeholder={t('login.password')}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <AccessibleButton
        testID="login-button"
        onPress={handleLogin}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('login.button')}
          </Text>
        )}
      </AccessibleButton>
      
      <TouchableOpacity
        testID="forgot-password-link"
        onPress={() => onNavigate?.('forgot-password')}
        style={{ marginBottom: 16 }}
      >
        <Text style={{ color: theme.colors.primary, textAlign: 'center' }}>
          {t('login.forgotPassword')}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        testID="register-link"
        onPress={() => onNavigate?.('register')}
        style={{ marginBottom: 16 }}
      >
        <Text style={{ color: theme.colors.primary, textAlign: 'center' }}>
          {t('login.register')}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        testID="biometric-login-button"
        onPress={handleBiometricLogin}
        style={{
          borderWidth: 1,
          borderColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        <Text style={{ color: theme.colors.primary, fontWeight: 'bold' }}>
          {t('login.biometric')}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderRegisterScreen = () => (
    <View testID="register-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('register.title')}
      </Text>
      
      <TextInput
        testID="name-input"
        placeholder={t('register.name')}
        value={name}
        onChangeText={setName}
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="email-input"
        placeholder={t('register.email')}
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="password-input"
        placeholder={t('register.password')}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="confirm-password-input"
        placeholder={t('register.confirmPassword')}
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <AccessibleButton
        testID="register-button"
        onPress={handleRegister}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('register.button')}
          </Text>
        )}
      </AccessibleButton>
    </View>
  );

  const renderHomeScreen = () => (
    <View testID="home-screen" style={{ flex: 1 }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 }}>
        <TouchableOpacity
          testID="drawer-toggle-button"
          onPress={() => setShowDrawer(!showDrawer)}
          style={{ padding: 8 }}
        >
          <Text style={{ fontSize: 18, color: theme.colors.text }}>☰</Text>
        </TouchableOpacity>
        
        <Text style={{ fontSize: 20, fontWeight: 'bold', color: theme.colors.text }}>
          {t('home.title')}
        </Text>
        
        <TouchableOpacity
          testID="search-button"
          onPress={handleSearch}
          style={{ padding: 8 }}
        >
          <Text style={{ fontSize: 18, color: theme.colors.text }}>🔍</Text>
        </TouchableOpacity>
      </View>
      
      <FlatList
        testID="home-list"
        data={listItems}
        renderItem={renderListItem}
        keyExtractor={(item) => item.id.toString()}
        refreshing={refreshing}
        onRefresh={handlePullToRefresh}
        style={{ flex: 1 }}
      />
      
      <TouchableOpacity
        testID="add-item-button"
        onPress={() => setIsModalVisible(true)}
        style={{
          position: 'absolute',
          bottom: 20,
          right: 20,
          backgroundColor: theme.colors.primary,
          width: 56,
          height: 56,
          borderRadius: 28,
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Text style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>+</Text>
      </TouchableOpacity>
    </View>
  );

  const renderProfileScreen = () => (
    <View testID="profile-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('profile.title')}
      </Text>
      
      <TextInput
        testID="name-input"
        placeholder={t('profile.name')}
        value={name}
        onChangeText={setName}
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="email-input"
        placeholder={t('profile.email')}
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <AccessibleButton
        testID="save-button"
        onPress={handleSaveSettings}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('profile.save')}
          </Text>
        )}
      </AccessibleButton>
      
      <TouchableOpacity
        testID="user-profile-button"
        onPress={() => setShowDrawer(true)}
        style={{
          marginTop: 20,
          padding: 16,
          backgroundColor: theme.colors.surface,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        <Text style={{ color: theme.colors.text }}>
          {t('profile.menu')}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderSettingsScreen = () => (
    <View testID="settings-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('settings.title')}
      </Text>
      
      <TextInput
        testID="api-key-input"
        placeholder={t('settings.apiKey')}
        value={apiKey}
        onChangeText={setApiKey}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 16 }}>
        <Text style={{ flex: 1, color: theme.colors.text }}>
          {t('settings.notifications')}
        </Text>
        <Switch
          testID="notifications-switch"
          value={isSwitchOn}
          onValueChange={setIsSwitchOn}
        />
      </View>
      
      <AccessibleButton
        testID="submit-button"
        onPress={handleSaveSettings}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('settings.save')}
          </Text>
        )}
      </AccessibleButton>
    </View>
  );

  const renderDetailScreen = () => (
    <View testID="detail-screen" style={{ flex: 1, padding: 20 }}>
      <TouchableOpacity
        testID="back-button"
        onPress={() => onNavigate?.('home')}
        style={{ marginBottom: 20 }}
      >
        <Text style={{ color: theme.colors.primary, fontSize: 16 }}>
          ← {t('common.back')}
        </Text>
      </TouchableOpacity>
      
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('detail.title')}
      </Text>
      
      <Image
        testID="detail-image"
        source={{ uri: 'https://picsum.photos/400/300?random=1' }}
        style={{ width: '100%', height: 200, borderRadius: 8, marginBottom: 20 }}
        resizeMode="cover"
      />
      
      <TouchableOpacity
        testID="detail-action-button"
        onPress={() => onNavigate?.('sub-detail')}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        <Text style={{ color: 'white', fontWeight: 'bold' }}>
          {t('detail.action')}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderModal = () => (
    <Modal
      testID="add-item-modal"
      visible={isModalVisible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={{ flex: 1, padding: 20 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <Text style={{ fontSize: 20, fontWeight: 'bold', color: theme.colors.text }}>
            {t('modal.addItem')}
          </Text>
          <TouchableOpacity
            testID="close-modal-button"
            onPress={() => setIsModalVisible(false)}
          >
            <Text style={{ fontSize: 18, color: theme.colors.text }}>✕</Text>
          </TouchableOpacity>
        </View>
        
        <TextInput
          testID="modal-title-input"
          placeholder={t('modal.title')}
          value={modalTitle}
          onChangeText={setModalTitle}
          style={{
            borderWidth: 1,
            borderColor: theme.colors.border,
            borderRadius: 8,
            padding: 12,
            marginBottom: 16,
            color: theme.colors.text,
          }}
        />
        
        <TextInput
          testID="modal-description-input"
          placeholder={t('modal.description')}
          value={modalDescription}
          onChangeText={setModalDescription}
          multiline
          numberOfLines={4}
          style={{
            borderWidth: 1,
            borderColor: theme.colors.border,
            borderRadius: 8,
            padding: 12,
            marginBottom: 20,
            color: theme.colors.text,
            textAlignVertical: 'top',
          }}
        />
        
        <AccessibleButton
          testID="modal-save-button"
          onPress={handleModalSave}
          disabled={isLoading}
          style={{
            backgroundColor: theme.colors.primary,
            padding: 16,
            borderRadius: 8,
            alignItems: 'center',
          }}
        >
          {isLoading ? (
            <ActivityIndicator testID="loading-indicator" color="white" />
          ) : (
            <Text style={{ color: 'white', fontWeight: 'bold' }}>
              {t('modal.save')}
            </Text>
          )}
        </AccessibleButton>
      </SafeAreaView>
    </Modal>
  );

  const renderDrawer = () => (
    <Modal
      testID="drawer-menu"
      visible={showDrawer}
      animationType="slide"
      transparent
    >
      <View style={{ flex: 1, flexDirection: 'row' }}>
        <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <TouchableOpacity
            testID="drawer-overlay"
            style={{ flex: 1 }}
            onPress={() => setShowDrawer(false)}
          />
        </View>
        <View style={{ width: screenWidth * 0.8, backgroundColor: theme.colors.surface }}>
          <SafeAreaView style={{ flex: 1, padding: 20 }}>
            <Text style={{ fontSize: 20, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
              {t('drawer.title')}
            </Text>
            
            <TouchableOpacity
              testID="drawer-help-item"
              onPress={() => {
                setShowDrawer(false);
                onNavigate?.('help');
              }}
              style={{ padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border }}
            >
              <Text style={{ color: theme.colors.text }}>
                {t('drawer.help')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              testID="logout-button"
              onPress={handleLogout}
              style={{ padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border }}
            >
              <Text style={{ color: theme.colors.error }}>
                {t('drawer.logout')}
              </Text>
            </TouchableOpacity>
          </SafeAreaView>
        </View>
      </View>
    </Modal>
  );

  const renderSearchModal = () => (
    <Modal
      testID="search-modal"
      visible={showSearch}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={{ flex: 1, padding: 20 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <Text style={{ fontSize: 20, fontWeight: 'bold', color: theme.colors.text }}>
            {t('search.title')}
          </Text>
          <TouchableOpacity
            testID="close-search-button"
            onPress={() => setShowSearch(false)}
          >
            <Text style={{ fontSize: 18, color: theme.colors.text }}>✕</Text>
          </TouchableOpacity>
        </View>
        
        <TextInput
          testID="search-input"
          placeholder={t('search.placeholder')}
          value={searchQuery}
          onChangeText={setSearchQuery}
          style={{
            borderWidth: 1,
            borderColor: theme.colors.border,
            borderRadius: 8,
            padding: 12,
            marginBottom: 16,
            color: theme.colors.text,
          }}
        />
        
        <TouchableOpacity
          testID="search-filter-button"
          onPress={() => setShowSearch(false)}
          style={{
            backgroundColor: theme.colors.primary,
            padding: 16,
            borderRadius: 8,
            alignItems: 'center',
            marginBottom: 16,
          }}
        >
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('search.filter')}
          </Text>
        </TouchableOpacity>
        
        <View testID="search-results" style={{ flex: 1 }}>
          <Text style={{ color: theme.colors.text }}>
            {t('search.results')}
          </Text>
        </View>
      </SafeAreaView>
    </Modal>
  );

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'login':
        return renderLoginScreen();
      case 'register':
        return renderRegisterScreen();
      case 'home':
        return renderHomeScreen();
      case 'profile':
        return renderProfileScreen();
      case 'settings':
        return renderSettingsScreen();
      case 'detail':
        return renderDetailScreen();
      default:
        return renderHomeScreen();
    }
  };

  return (
    <ErrorBoundary>
      <SafeAreaView style={{ flex: 1, backgroundColor: theme.colors.background }}>
        <View style={{ flex: 1, flexDirection: 'row' }}>
          {/* Tab Navigation */}
          <View style={{ 
            width: 80, 
            backgroundColor: theme.colors.surface, 
            borderRightWidth: 1, 
            borderRightColor: theme.colors.border 
          }}>
            <TouchableOpacity
              testID="home-tab"
              onPress={() => setCurrentScreen('home')}
              style={{ 
                padding: 16, 
                alignItems: 'center',
                backgroundColor: currentScreen === 'home' ? theme.colors.primary : 'transparent'
              }}
            >
              <Text style={{ 
                color: currentScreen === 'home' ? 'white' : theme.colors.text,
                fontSize: 12,
                textAlign: 'center'
              }}>
                {t('tabs.home')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              testID="profile-tab"
              onPress={() => setCurrentScreen('profile')}
              style={{ 
                padding: 16, 
                alignItems: 'center',
                backgroundColor: currentScreen === 'profile' ? theme.colors.primary : 'transparent'
              }}
            >
              <Text style={{ 
                color: currentScreen === 'profile' ? 'white' : theme.colors.text,
                fontSize: 12,
                textAlign: 'center'
              }}>
                {t('tabs.profile')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              testID="settings-tab"
              onPress={() => setCurrentScreen('settings')}
              style={{ 
                padding: 16, 
                alignItems: 'center',
                backgroundColor: currentScreen === 'settings' ? theme.colors.primary : 'transparent'
              }}
            >
              <Text style={{ 
                color: currentScreen === 'settings' ? 'white' : theme.colors.text,
                fontSize: 12,
                textAlign: 'center'
              }}>
                {t('tabs.settings')}
              </Text>
            </TouchableOpacity>
          </View>
          
          {/* Main Content */}
          <View style={{ flex: 1 }}>
            {renderCurrentScreen()}
          </View>
        </View>
        
        {/* Modals */}
        {renderModal()}
        {renderDrawer()}
        {renderSearchModal()}
      </SafeAreaView>
    </ErrorBoundary>
  );
}
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Modal,
  Alert,
  Switch,
  FlatList,
  Image,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';
import { useOptimizedPerformance } from '../../hooks/performance/use-optimized-performance';
import { validateFormData } from '../../lib/validation/validation-schemas';
import { secureStorage } from '../../lib/security/secure-storage';
import { AccessibleButton } from '../accessibility/accessible-button';
import { ErrorBoundary } from '../error-boundary/error-boundary';

interface TestableComponentProps {
  onNavigate?: (screen: string) => void;
  onShowModal?: (modalType: string) => void;
}

interface ListItem {
  id: number;
  title: string;
  description: string;
  imageUrl?: string;
}

const { width: screenWidth } = Dimensions.get('window');

export function DetoxTestableComponents({ onNavigate, onShowModal }: TestableComponentProps) {
  const { t } = useI18n();
  const { theme, user, notifications } = useAppStore();
  const { trackRender, trackInteraction } = useOptimizedPerformance();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [modalDescription, setModalDescription] = useState('');
  const [isSwitchOn, setIsSwitchOn] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState(0);
  const [showSearch, setShowSearch] = useState(false);
  const [showDrawer, setShowDrawer] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('home');
  const [listItems, setListItems] = useState<ListItem[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // Track component renders for performance testing
  trackRender('DetoxTestableComponents');

  // Mock data for list items
  const mockListItems: ListItem[] = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    title: `Item ${i + 1}`,
    description: `Description for item ${i + 1}`,
    imageUrl: `https://picsum.photos/200/200?random=${i}`,
  }));

  const handleLogin = useCallback(async () => {
    trackInteraction('login_attempt');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validate form data
      const formData = { email, password };
      const validation = validateFormData('login', formData);
      
      if (!validation.success) {
        // Show validation errors
        return;
      }
      
      // Simulate successful login
      onNavigate?.('home');
    } catch (error) {
      // Handle login error
    } finally {
      setIsLoading(false);
    }
  }, [email, password, onNavigate, trackInteraction]);

  const handleRegister = useCallback(async () => {
    trackInteraction('register_attempt');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validate form data
      const formData = { name, email, password, confirmPassword };
      const validation = validateFormData('register', formData);
      
      if (!validation.success) {
        // Show validation errors
        return;
      }
      
      // Simulate successful registration
      onNavigate?.('home');
    } catch (error) {
      // Handle registration error
    } finally {
      setIsLoading(false);
    }
  }, [name, email, password, confirmPassword, onNavigate, trackInteraction]);

  const handleLogout = useCallback(async () => {
    trackInteraction('logout_attempt');
    
    Alert.alert(
      'Confirm Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await secureStorage.removeItem('authToken');
              onNavigate?.('login');
            } catch (error) {
              // Handle logout error
            }
          },
        },
      ]
    );
  }, [onNavigate, trackInteraction]);

  const handleSaveSettings = useCallback(async () => {
    trackInteraction('save_settings');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Save API key securely
      await secureStorage.setItem('apiKey', apiKey);
      
      // Show success message
    } catch (error) {
      // Handle save error
    } finally {
      setIsLoading(false);
    }
  }, [apiKey, trackInteraction]);

  const handleSearch = useCallback(() => {
    trackInteraction('search_performed');
    setShowSearch(true);
  }, [trackInteraction]);

  const handleApplyFilter = useCallback(() => {
    trackInteraction('filter_applied');
    setShowSearch(false);
  }, [trackInteraction]);

  const handlePullToRefresh = useCallback(async () => {
    trackInteraction('pull_to_refresh');
    setRefreshing(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setListItems(mockListItems);
    } catch (error) {
      // Handle refresh error
    } finally {
      setRefreshing(false);
    }
  }, [trackInteraction]);

  const handleListItemPress = useCallback((item: ListItem) => {
    trackInteraction('list_item_pressed');
    onNavigate?.('detail');
  }, [onNavigate, trackInteraction]);

  const handleSwipeAction = useCallback((item: ListItem) => {
    trackInteraction('swipe_action');
    // Handle swipe action
  }, [trackInteraction]);

  const handleLongPress = useCallback((item: ListItem) => {
    trackInteraction('long_press');
    // Show context menu
  }, [trackInteraction]);

  const handleModalSave = useCallback(async () => {
    trackInteraction('modal_save');
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setIsModalVisible(false);
      setModalTitle('');
      setModalDescription('');
    } catch (error) {
      // Handle save error
    } finally {
      setIsLoading(false);
    }
  }, [trackInteraction]);

  const handleBiometricLogin = useCallback(async () => {
    trackInteraction('biometric_login');
    try {
      // Simulate biometric authentication
      await new Promise(resolve => setTimeout(resolve, 500));
      onNavigate?.('home');
    } catch (error) {
      // Handle biometric error
    }
  }, [onNavigate, trackInteraction]);

  const renderListItem = useCallback(({ item }: { item: ListItem }) => (
    <TouchableOpacity
      testID={`home-list-item-${item.id}`}
      onPress={() => handleListItemPress(item)}
      onLongPress={() => handleLongPress(item)}
      style={{
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.border,
        flexDirection: 'row',
        alignItems: 'center',
      }}
    >
      {item.imageUrl && (
        <Image
          testID={`item-image-${item.id}`}
          source={{ uri: item.imageUrl }}
          style={{ width: 50, height: 50, borderRadius: 25, marginRight: 12 }}
          resizeMode="cover"
        />
      )}
      <View style={{ flex: 1 }}>
        <Text style={{ fontSize: 16, fontWeight: 'bold', color: theme.colors.text }}>
          {item.title}
        </Text>
        <Text style={{ fontSize: 14, color: theme.colors.textSecondary }}>
          {item.description}
        </Text>
      </View>
    </TouchableOpacity>
  ), [theme.colors, handleListItemPress, handleLongPress]);

  const renderLoginScreen = () => (
    <View testID="login-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('login.title')}
      </Text>
      
      <TextInput
        testID="email-input"
        placeholder={t('login.email')}
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="password-input"
        placeholder={t('login.password')}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <AccessibleButton
        testID="login-button"
        onPress={handleLogin}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('login.button')}
          </Text>
        )}
      </AccessibleButton>
      
      <TouchableOpacity
        testID="forgot-password-link"
        onPress={() => onNavigate?.('forgot-password')}
        style={{ marginBottom: 16 }}
      >
        <Text style={{ color: theme.colors.primary, textAlign: 'center' }}>
          {t('login.forgotPassword')}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        testID="register-link"
        onPress={() => onNavigate?.('register')}
        style={{ marginBottom: 16 }}
      >
        <Text style={{ color: theme.colors.primary, textAlign: 'center' }}>
          {t('login.register')}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        testID="biometric-login-button"
        onPress={handleBiometricLogin}
        style={{
          borderWidth: 1,
          borderColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        <Text style={{ color: theme.colors.primary, fontWeight: 'bold' }}>
          {t('login.biometric')}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderRegisterScreen = () => (
    <View testID="register-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('register.title')}
      </Text>
      
      <TextInput
        testID="name-input"
        placeholder={t('register.name')}
        value={name}
        onChangeText={setName}
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="email-input"
        placeholder={t('register.email')}
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="password-input"
        placeholder={t('register.password')}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="confirm-password-input"
        placeholder={t('register.confirmPassword')}
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <AccessibleButton
        testID="register-button"
        onPress={handleRegister}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('register.button')}
          </Text>
        )}
      </AccessibleButton>
    </View>
  );

  const renderHomeScreen = () => (
    <View testID="home-screen" style={{ flex: 1 }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 }}>
        <TouchableOpacity
          testID="drawer-toggle-button"
          onPress={() => setShowDrawer(!showDrawer)}
          style={{ padding: 8 }}
        >
          <Text style={{ fontSize: 18, color: theme.colors.text }}>☰</Text>
        </TouchableOpacity>
        
        <Text style={{ fontSize: 20, fontWeight: 'bold', color: theme.colors.text }}>
          {t('home.title')}
        </Text>
        
        <TouchableOpacity
          testID="search-button"
          onPress={handleSearch}
          style={{ padding: 8 }}
        >
          <Text style={{ fontSize: 18, color: theme.colors.text }}>🔍</Text>
        </TouchableOpacity>
      </View>
      
      <FlatList
        testID="home-list"
        data={listItems}
        renderItem={renderListItem}
        keyExtractor={(item) => item.id.toString()}
        refreshing={refreshing}
        onRefresh={handlePullToRefresh}
        style={{ flex: 1 }}
      />
      
      <TouchableOpacity
        testID="add-item-button"
        onPress={() => setIsModalVisible(true)}
        style={{
          position: 'absolute',
          bottom: 20,
          right: 20,
          backgroundColor: theme.colors.primary,
          width: 56,
          height: 56,
          borderRadius: 28,
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Text style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>+</Text>
      </TouchableOpacity>
    </View>
  );

  const renderProfileScreen = () => (
    <View testID="profile-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('profile.title')}
      </Text>
      
      <TextInput
        testID="name-input"
        placeholder={t('profile.name')}
        value={name}
        onChangeText={setName}
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <TextInput
        testID="email-input"
        placeholder={t('profile.email')}
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <AccessibleButton
        testID="save-button"
        onPress={handleSaveSettings}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('profile.save')}
          </Text>
        )}
      </AccessibleButton>
      
      <TouchableOpacity
        testID="user-profile-button"
        onPress={() => setShowDrawer(true)}
        style={{
          marginTop: 20,
          padding: 16,
          backgroundColor: theme.colors.surface,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        <Text style={{ color: theme.colors.text }}>
          {t('profile.menu')}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderSettingsScreen = () => (
    <View testID="settings-screen" style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('settings.title')}
      </Text>
      
      <TextInput
        testID="api-key-input"
        placeholder={t('settings.apiKey')}
        value={apiKey}
        onChangeText={setApiKey}
        secureTextEntry
        style={{
          borderWidth: 1,
          borderColor: theme.colors.border,
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
          color: theme.colors.text,
        }}
      />
      
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 16 }}>
        <Text style={{ flex: 1, color: theme.colors.text }}>
          {t('settings.notifications')}
        </Text>
        <Switch
          testID="notifications-switch"
          value={isSwitchOn}
          onValueChange={setIsSwitchOn}
        />
      </View>
      
      <AccessibleButton
        testID="submit-button"
        onPress={handleSaveSettings}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        {isLoading ? (
          <ActivityIndicator testID="loading-indicator" color="white" />
        ) : (
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('settings.save')}
          </Text>
        )}
      </AccessibleButton>
    </View>
  );

  const renderDetailScreen = () => (
    <View testID="detail-screen" style={{ flex: 1, padding: 20 }}>
      <TouchableOpacity
        testID="back-button"
        onPress={() => onNavigate?.('home')}
        style={{ marginBottom: 20 }}
      >
        <Text style={{ color: theme.colors.primary, fontSize: 16 }}>
          ← {t('common.back')}
        </Text>
      </TouchableOpacity>
      
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
        {t('detail.title')}
      </Text>
      
      <Image
        testID="detail-image"
        source={{ uri: 'https://picsum.photos/400/300?random=1' }}
        style={{ width: '100%', height: 200, borderRadius: 8, marginBottom: 20 }}
        resizeMode="cover"
      />
      
      <TouchableOpacity
        testID="detail-action-button"
        onPress={() => onNavigate?.('sub-detail')}
        style={{
          backgroundColor: theme.colors.primary,
          padding: 16,
          borderRadius: 8,
          alignItems: 'center',
        }}
      >
        <Text style={{ color: 'white', fontWeight: 'bold' }}>
          {t('detail.action')}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderModal = () => (
    <Modal
      testID="add-item-modal"
      visible={isModalVisible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={{ flex: 1, padding: 20 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <Text style={{ fontSize: 20, fontWeight: 'bold', color: theme.colors.text }}>
            {t('modal.addItem')}
          </Text>
          <TouchableOpacity
            testID="close-modal-button"
            onPress={() => setIsModalVisible(false)}
          >
            <Text style={{ fontSize: 18, color: theme.colors.text }}>✕</Text>
          </TouchableOpacity>
        </View>
        
        <TextInput
          testID="modal-title-input"
          placeholder={t('modal.title')}
          value={modalTitle}
          onChangeText={setModalTitle}
          style={{
            borderWidth: 1,
            borderColor: theme.colors.border,
            borderRadius: 8,
            padding: 12,
            marginBottom: 16,
            color: theme.colors.text,
          }}
        />
        
        <TextInput
          testID="modal-description-input"
          placeholder={t('modal.description')}
          value={modalDescription}
          onChangeText={setModalDescription}
          multiline
          numberOfLines={4}
          style={{
            borderWidth: 1,
            borderColor: theme.colors.border,
            borderRadius: 8,
            padding: 12,
            marginBottom: 20,
            color: theme.colors.text,
            textAlignVertical: 'top',
          }}
        />
        
        <AccessibleButton
          testID="modal-save-button"
          onPress={handleModalSave}
          disabled={isLoading}
          style={{
            backgroundColor: theme.colors.primary,
            padding: 16,
            borderRadius: 8,
            alignItems: 'center',
          }}
        >
          {isLoading ? (
            <ActivityIndicator testID="loading-indicator" color="white" />
          ) : (
            <Text style={{ color: 'white', fontWeight: 'bold' }}>
              {t('modal.save')}
            </Text>
          )}
        </AccessibleButton>
      </SafeAreaView>
    </Modal>
  );

  const renderDrawer = () => (
    <Modal
      testID="drawer-menu"
      visible={showDrawer}
      animationType="slide"
      transparent
    >
      <View style={{ flex: 1, flexDirection: 'row' }}>
        <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <TouchableOpacity
            testID="drawer-overlay"
            style={{ flex: 1 }}
            onPress={() => setShowDrawer(false)}
          />
        </View>
        <View style={{ width: screenWidth * 0.8, backgroundColor: theme.colors.surface }}>
          <SafeAreaView style={{ flex: 1, padding: 20 }}>
            <Text style={{ fontSize: 20, fontWeight: 'bold', marginBottom: 20, color: theme.colors.text }}>
              {t('drawer.title')}
            </Text>
            
            <TouchableOpacity
              testID="drawer-help-item"
              onPress={() => {
                setShowDrawer(false);
                onNavigate?.('help');
              }}
              style={{ padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border }}
            >
              <Text style={{ color: theme.colors.text }}>
                {t('drawer.help')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              testID="logout-button"
              onPress={handleLogout}
              style={{ padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border }}
            >
              <Text style={{ color: theme.colors.error }}>
                {t('drawer.logout')}
              </Text>
            </TouchableOpacity>
          </SafeAreaView>
        </View>
      </View>
    </Modal>
  );

  const renderSearchModal = () => (
    <Modal
      testID="search-modal"
      visible={showSearch}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={{ flex: 1, padding: 20 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <Text style={{ fontSize: 20, fontWeight: 'bold', color: theme.colors.text }}>
            {t('search.title')}
          </Text>
          <TouchableOpacity
            testID="close-search-button"
            onPress={() => setShowSearch(false)}
          >
            <Text style={{ fontSize: 18, color: theme.colors.text }}>✕</Text>
          </TouchableOpacity>
        </View>
        
        <TextInput
          testID="search-input"
          placeholder={t('search.placeholder')}
          value={searchQuery}
          onChangeText={setSearchQuery}
          style={{
            borderWidth: 1,
            borderColor: theme.colors.border,
            borderRadius: 8,
            padding: 12,
            marginBottom: 16,
            color: theme.colors.text,
          }}
        />
        
        <TouchableOpacity
          testID="search-filter-button"
          onPress={() => setShowSearch(false)}
          style={{
            backgroundColor: theme.colors.primary,
            padding: 16,
            borderRadius: 8,
            alignItems: 'center',
            marginBottom: 16,
          }}
        >
          <Text style={{ color: 'white', fontWeight: 'bold' }}>
            {t('search.filter')}
          </Text>
        </TouchableOpacity>
        
        <View testID="search-results" style={{ flex: 1 }}>
          <Text style={{ color: theme.colors.text }}>
            {t('search.results')}
          </Text>
        </View>
      </SafeAreaView>
    </Modal>
  );

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'login':
        return renderLoginScreen();
      case 'register':
        return renderRegisterScreen();
      case 'home':
        return renderHomeScreen();
      case 'profile':
        return renderProfileScreen();
      case 'settings':
        return renderSettingsScreen();
      case 'detail':
        return renderDetailScreen();
      default:
        return renderHomeScreen();
    }
  };

  return (
    <ErrorBoundary>
      <SafeAreaView style={{ flex: 1, backgroundColor: theme.colors.background }}>
        <View style={{ flex: 1, flexDirection: 'row' }}>
          {/* Tab Navigation */}
          <View style={{ 
            width: 80, 
            backgroundColor: theme.colors.surface, 
            borderRightWidth: 1, 
            borderRightColor: theme.colors.border 
          }}>
            <TouchableOpacity
              testID="home-tab"
              onPress={() => setCurrentScreen('home')}
              style={{ 
                padding: 16, 
                alignItems: 'center',
                backgroundColor: currentScreen === 'home' ? theme.colors.primary : 'transparent'
              }}
            >
              <Text style={{ 
                color: currentScreen === 'home' ? 'white' : theme.colors.text,
                fontSize: 12,
                textAlign: 'center'
              }}>
                {t('tabs.home')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              testID="profile-tab"
              onPress={() => setCurrentScreen('profile')}
              style={{ 
                padding: 16, 
                alignItems: 'center',
                backgroundColor: currentScreen === 'profile' ? theme.colors.primary : 'transparent'
              }}
            >
              <Text style={{ 
                color: currentScreen === 'profile' ? 'white' : theme.colors.text,
                fontSize: 12,
                textAlign: 'center'
              }}>
                {t('tabs.profile')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              testID="settings-tab"
              onPress={() => setCurrentScreen('settings')}
              style={{ 
                padding: 16, 
                alignItems: 'center',
                backgroundColor: currentScreen === 'settings' ? theme.colors.primary : 'transparent'
              }}
            >
              <Text style={{ 
                color: currentScreen === 'settings' ? 'white' : theme.colors.text,
                fontSize: 12,
                textAlign: 'center'
              }}>
                {t('tabs.settings')}
              </Text>
            </TouchableOpacity>
          </View>
          
          {/* Main Content */}
          <View style={{ flex: 1 }}>
            {renderCurrentScreen()}
          </View>
        </View>
        
        {/* Modals */}
        {renderModal()}
        {renderDrawer()}
        {renderSearchModal()}
      </SafeAreaView>
    </ErrorBoundary>
  );
}


