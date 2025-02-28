import { useState, useRef, useCallback, JSX } from "react";
import Webcam from "react-webcam";
import {
  Button,
  Paper,
  Stack,
  Group,
  Image,
  Text,
  Container,
  Loader,
} from "@mantine/core";
import { IconCamera, IconRefresh, IconCheck } from "@tabler/icons-react";

interface WebcamComponentProps {
  imageUrl: string;
  setFieldValue: (value: string) => void;
}

const videoConstraints = {
  facingMode: "user",
};

function WebcamComponent({
  imageUrl,
  setFieldValue,
}: WebcamComponentProps): JSX.Element {
  const webcamRef = useRef<Webcam>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showCamera, setShowCamera] = useState<boolean>(true);
  const [rederWebCamm, setRederWebCamm] = useState<boolean>(false);

  const capture = useCallback(() => {
    if (webcamRef.current) {
      setIsLoading(true);
      const imageSrc = webcamRef.current.getScreenshot();
      setIsLoading(false);
      if (imageSrc) {
        setCapturedImage(imageSrc);
        setFieldValue(imageSrc);
      }
    }
  }, [webcamRef]);

  const retakePhoto = useCallback(() => {
    setCapturedImage(null);
    setFieldValue("");
  }, [setFieldValue]);

  const confirmPhoto = useCallback(() => {
    setShowCamera(false);
  }, [setShowCamera]);

  if (imageUrl !== "" && !showCamera) {
    return (
      <Container>
        <Image src={imageUrl} alt="caputured Image" height="200rem" />
      </Container>
    );
  }

  if (!rederWebCamm) {
    return <Button onClick={() => setRederWebCamm(true)}>Upload photo</Button>;
  }

  if (isLoading) {
    return (
      <Container size="md" p="xl">
        <Paper p="xl" radius="md" withBorder shadow="md">
          <Stack align="center" p="md">
            <Loader size="xl" />
            <Text>Loading camera...</Text>
          </Stack>
        </Paper>
      </Container>
    );
  }
  return (
    <>
      {showCamera ? (
        <Container size="md" p="xl">
          {capturedImage ? (
            <Stack p="md" align="center">
              <Paper withBorder p="xs" radius="md" shadow="sm">
                <Image
                  src={capturedImage}
                  alt="Captured photo"
                  radius="md"
                  height={500}
                  width={500}
                  fit="contain"
                />
              </Paper>

              <Group align="center" p="md">
                <Button
                  leftSection={<IconRefresh size={18} />}
                  color="red"
                  variant="filled"
                  onClick={retakePhoto}
                >
                  Retake Photo
                </Button>
                <Button
                  leftSection={<IconCheck size={18} />}
                  color="green"
                  variant="filled"
                  onClick={confirmPhoto}
                >
                  Use This Photo
                </Button>
              </Group>
            </Stack>
          ) : (
            <Stack p="md" align="center">
              <Paper withBorder p="xs" radius="md" shadow="sm">
                <Webcam
                  audio={false}
                  height={500}
                  width={500}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  videoConstraints={videoConstraints}
                  onUserMediaError={() => {
                    setFieldValue("");
                  }}
                />
              </Paper>

              <Button
                leftSection={<IconCamera size={18} />}
                color="blue"
                variant="filled"
                size="md"
                onClick={capture}
              >
                Capture Photo
              </Button>
            </Stack>
          )}
        </Container>
      ) : (
        <Container>
          <Image src={imageUrl} alt="caputured Image" height="200rem" />
        </Container>
      )}
    </>
  );
}

export default WebcamComponent;
