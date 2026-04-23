import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#0a0a0f' },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 20,
        paddingVertical: 15,
    },
    backBtn: { padding: 4 },
    headerTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
    body: { paddingHorizontal: 20, paddingBottom: 100 },

    // 영상 화면
    mediaPreview: {
        width: '100%',
        height: 200,
        borderRadius: 20,
        overflow: 'hidden',
        backgroundColor: '#161622',
        marginBottom: 24,
        position: 'relative',
    },
    previewImage: { width: '100%', height: '100%' },
    mediaOverlay: {
        position: 'absolute',
        top: 16,
        left: 16,
    },
    statusBadge: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 8,
    },
    statusBadgeText: { color: '#fff', fontSize: 12, fontWeight: '900' },

    // 신뢰도
    scoreSection: { marginBottom: 24 },
    scoreInfo: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 8 },
    scoreLabel: { color: '#444468', fontSize: 14 },
    scoreValue: { fontSize: 24, fontWeight: 'bold' },
    gaugeBar: { width: '100%', height: 8, backgroundColor: '#1e1e2e', borderRadius: 4 },
    gaugeFill: { height: '100%', borderRadius: 4 },

    // 분석 근거
    reasonCard: {
        backgroundColor: '#161622',
        borderRadius: 20,
        padding: 20,
        marginBottom: 16,
        borderWidth: 1,
        borderColor: '#1e1e2e'
    },
    reasonTitle: { color: '#7c6cfa', fontSize: 13, fontWeight: 'bold', marginBottom: 12 },
    reasonContent: { color: '#e1e1e6', fontSize: 15, lineHeight: 24 },

    // 기타 
    detailGrid: { flexDirection: 'row', gap: 12, marginBottom: 24 },
    detailItem: { flex: 1, backgroundColor: '#11111d', padding: 16, borderRadius: 16, alignItems: 'center' },
    detailLabel: { color: '#444468', fontSize: 12, marginBottom: 4 },
    detailValue: { fontSize: 15, fontWeight: 'bold' },
    textFake: { color: '#ff453a' },
    textReal: { color: '#32d74b' },
    bgFake: { backgroundColor: '#ff453a' },
    bgReal: { backgroundColor: '#32d74b' },

    shareBtn: {
        flexDirection: 'row',
        backgroundColor: '#1a1a2e',
        height: 56,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
    },
    shareBtnText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});