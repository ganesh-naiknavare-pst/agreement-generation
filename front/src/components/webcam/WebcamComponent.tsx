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
import {
  IconCamera,
  IconRefresh,
  IconCheck,
  IconCircleCheck,
} from "@tabler/icons-react";
import { COLORS } from "../../colors";
import * as blazeface from "@tensorflow-models/blazeface";
import "@tensorflow/tfjs";

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
  const [capturedImage, setCapturedImage] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [rederWebCamm, setRederWebCamm] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [buttonLoading, setButtonLoading] = useState<boolean>(false);

  const detectFaces = async (imageSrc: string) => {
    const model = await blazeface.load();

    return new Promise<number>((resolve) => {
      const img = document.createElement("img");
      img.src = imageSrc;

      img.onload = async () => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        canvas.width = img.width;
        canvas.height = img.height;
        ctx?.drawImage(img, 0, 0, img.width, img.height);

        const predictions = await model.estimateFaces(canvas, false);
        resolve(predictions.length);
      };

      img.onerror = () => resolve(0);
    });
  };

  const capture = useCallback(async () => {
    setError("");
    if (webcamRef.current) {
      setIsLoading(true);
      setButtonLoading(true);
      const imageSrc = webcamRef.current.getScreenshot();
      setIsLoading(false);
      if (imageSrc) {
        const faceCount = await detectFaces(imageSrc);

        if (faceCount > 1) {
          setError(
            "Multiple faces detected! Please ensure only one face is visible."
          );
          setButtonLoading(false);
          return;
        } else if (faceCount === 0) {
          setError(
            "No face detected! Please ensure your face is clearly visible."
          );
          setButtonLoading(false);
          return;
        }
        setCapturedImage(imageSrc);
        setButtonLoading(false);
      }
    }
  }, [webcamRef]);

  const retakePhoto = useCallback(() => {
    setCapturedImage("");
  }, [setCapturedImage]);

  const confirmPhoto = useCallback(() => {
    setFieldValue(capturedImage);
  }, [setFieldValue]);

  if (!rederWebCamm && imageUrl == "") {
    return (
      <Button
        leftSection={<IconCamera />}
        variant="outline"
        size="sm"
        onClick={() => setRederWebCamm(true)}
      >
        Start webcam
      </Button>
    );
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
      {imageUrl == "" ? (
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
              <Paper
                withBorder
                p="xs"
                radius="md"
                shadow="sm"
                style={{ border: error ? "2px solid red" : "none" }}
              >
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

              {error && <Text style={{ color: "red" }}>{error}</Text>}
              <Button
                leftSection={
                  !buttonLoading ? <IconCamera size={18} /> : undefined
                }
                color="blue"
                variant="filled"
                size="md"
                onClick={capture}
                loading={buttonLoading}
              >
                {buttonLoading ? "Processing..." : "Capture Photo"}
              </Button>
            </Stack>
          )}
        </Container>
      ) : (
        <Group>
          <IconCircleCheck color={COLORS.green} />
          <Paper
            p="sm"
            radius="md"
            withBorder
            shadow="md"
            style={{ borderColor: COLORS.green }}
          >
            <Image src={imageUrl} alt="caputured Image" height="200rem" />
          </Paper>
        </Group>
      )}
    </>
  );
}

export default WebcamComponent;
