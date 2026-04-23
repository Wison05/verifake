import React, { useState } from 'react';
import { View, Text, SafeAreaView, TouchableOpacity, Image, TextInput, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as VideoThumbnails from 'expo-video-thumbnails';
import { CloudArrowUpIcon, LinkIcon, VideoCameraIcon } from 'react-native-heroicons/outline';
import { styles } from './DetectionScreen.styles';
import { BottomNavigation } from '../components/BottomNavigaton';

export const DetectionInputScreen = ({ navigation }: any) => {
    const [videoUri, setVideoUri] = useState<string | null>(null);
    const [thumbnailUri, setThumbnailUri] = useState<string | null>(null);
    const [url, setUrl] = useState('');

    const pickVideo = async () => {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();

        if (status !== 'granted') {
            Alert.alert('권한 거부', '영상을 업로드하려면 갤러리 접근 권한이 필요합니다.');
            return;
        }

        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Videos,
            quality: 1,
        });

        if (!result.canceled) {
            setThumbnailUri(null);
            const selectedUri = result.assets[0].uri;
            setVideoUri(selectedUri);

            try {
                const { uri } = await VideoThumbnails.getThumbnailAsync(selectedUri, {
                    time: 100,
                });
                const cacheBusterUri = `${uri}?t=${new Date().getTime()}`;
                setThumbnailUri(cacheBusterUri);
                console.log(cacheBusterUri);
            } catch (e) {
                console.warn(e);
                setThumbnailUri(null);
            }
        }
    };

    const handleStartAnalysis = () => {
        if (!videoUri && !url) {
            Alert.alert("알림", "분석할 영상이나 URL을 등록해주세요.");
            return;
        }
        navigation.navigate('Analysis', { videoUri, thumbnailUri });
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.content}>
                <Text style={styles.title}>새로운 탐지 시작</Text>
                <Text style={styles.subTitle}>분석할 영상 파일이나 링크를 등록해주세요</Text>

                {/* 파일 업로드 */}
                <TouchableOpacity
                    style={[styles.uploadBox, videoUri ? { borderColor: '#7c6cfa', borderStyle: 'solid' } : {}]}
                    onPress={pickVideo}
                >
                    {thumbnailUri ? (
                        <View style={{ width: '100%', height: '100%', borderRadius: 18, overflow: 'hidden' }}>
                            <Image source={{ uri: thumbnailUri }} style={{ width: '100%', height: '100%' }} />
                            <View style={{ position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.6)', padding: 10, alignItems: 'center' }}>
                                <Text style={{ color: '#fff', fontSize: 12 }}>다시 선택하려면 클릭하세요</Text>
                            </View>
                        </View>
                    ) : (
                        <View style={{ alignItems: 'center' }}>
                            <CloudArrowUpIcon size={48} color="#7c6cfa" strokeWidth={1.5} />
                            <Text style={styles.uploadText}>영상 선택하기</Text>
                            <Text style={styles.uploadSubText}>MP4, MOV 등 영상 파일 지원</Text>
                        </View>
                    )}
                </TouchableOpacity>

                <View style={styles.divider}>
                    <View style={styles.line} />
                    <Text style={styles.dividerText}>또는</Text>
                    <View style={styles.line} />
                </View>

                {/* URL 입력 */}
                <View style={styles.inputContainer}>
                    <LinkIcon size={20} color="#444468" style={styles.inputIcon} />
                    <TextInput
                        style={styles.input}
                        placeholder="영상 URL 주소를 붙여넣으세요"
                        placeholderTextColor="#444468"
                        value={url}
                        onChangeText={setUrl}
                    />
                </View>

                {/* 분석 버튼 */}
                <TouchableOpacity
                    style={[styles.startBtn, !url && { opacity: 0.8 }]}
                    onPress={handleStartAnalysis}
                >
                    <Text style={styles.startBtnText}>영상 분석 시작하기</Text>
                </TouchableOpacity>
            </View>

            <BottomNavigation activeRoute="DetectionInput" />
        </SafeAreaView>
    );
};