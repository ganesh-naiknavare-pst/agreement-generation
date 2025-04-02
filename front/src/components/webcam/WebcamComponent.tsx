import { useState, useRef, useCallback, JSX, useEffect } from "react";
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
import useApi, { BackendEndpoints } from "../../hooks/useApi";
import { useParams } from "react-router-dom";

interface WebcamComponentProps {
  imageUrl: string;
  setFieldValue: (value: string) => void;
}

interface ValidationData {
  message: string;
  status: number;
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
  const params = useParams();

  const { fetchData: validateCapturedImage, data: validationResponce } =
    useApi<ValidationData>(BackendEndpoints.ValidateImage);

  useEffect(() => {
    if (validationResponce) {
      if (validationResponce.status === 400) {
        setError(validationResponce.message);
      } else {
        setCapturedImage(webcamRef.current?.getScreenshot() || "");
      }
      setButtonLoading(false);
    }
  }, [validationResponce]);

  const capture = useCallback(async () => {
    setError("");
    if (webcamRef.current) {
      setIsLoading(true);
      setButtonLoading(true);
      const imageSrc = webcamRef.current.getScreenshot();
      setIsLoading(false);
      if (imageSrc) {
        await validateCapturedImage({
          method: "POST",
          data: { image_url: imageSrc, agreement_id: params.agreementId },
        });
      }
    }
  }, [webcamRef, validateCapturedImage]);

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
            <Loader />
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
