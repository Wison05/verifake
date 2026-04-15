import { View, Text, SafeAreaView, TouchableOpacity, StyleSheet } from 'react-native';

export const HomeScreen = () => {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>VeriFake</Text>
        <Text style={styles.sub}>AI deepfake detection platform</Text>
      </View>
      <View style={styles.body}>
        <TouchableOpacity style={styles.btn}>
          <Text style={styles.btnText}>영상 탐지 시작</Text>
        </TouchableOpacity>
        <Text style={styles.label}>최근 탐지 기록</Text>
        <View style={styles.empty}>
          <Text style={styles.emptyText}>아직 탐지 기록이 없어요</Text>
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  header: { paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 0.5, borderBottomColor: '#1e1e2e' },
  logo: { color: '#7c6cfa', fontSize: 20, fontFamily: 'Courier New' },
  sub: { color: '#444468', fontSize: 12, marginTop: 4 },
  body: { flex: 1, paddingHorizontal: 20, paddingTop: 24, gap: 16 },
  btn: { backgroundColor: '#7c6cfa', borderRadius: 16, paddingVertical: 16, alignItems: 'center' },
  btnText: { color: '#fff', fontWeight: '600' },
  label: { color: '#444468', fontSize: 11, textTransform: 'uppercase', letterSpacing: 2 },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  emptyText: { color: '#2a2a3e', fontSize: 14 },
});