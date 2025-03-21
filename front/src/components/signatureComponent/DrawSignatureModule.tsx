import React, { useState, useRef, useCallback } from "react";
import CanvasDraw from "react-canvas-draw";
import { GithubPicker, ColorResult } from "react-color";
import {
  Box,
  Button,
  Modal,
  Group,
  Popover,
  Text,
  Tooltip,
  Center,
  Paper,
  ActionIcon,
  Image,
} from "@mantine/core";
import {
  IconPalette,
  IconArrowBackUp,
  IconTrash,
  IconCheck,
} from "@tabler/icons-react";
import { COLORS } from "../../colors";

interface CanvasDrawExtended extends CanvasDraw {
  canvasContainer: {
    children: HTMLCanvasElement[];
  };
}

interface DrawSignatureModalProps {
  opened: boolean;
  onClose: () => void;
  onSave: (signatureData: string) => void;
}

const inkColors: string[] = [
  "#1976d2",
  "#0d47a1",
  "#000000",
  "#444444",
  "#0000ff",
  "#000080",
  "#191970",
  "#00008b",
  "#483d8b",
  "#4169e1",
];

const DrawSignatureModal: React.FC<DrawSignatureModalProps> = ({
  opened,
  onClose,
  onSave,
}) => {
  const canvasRef = useRef<CanvasDrawExtended>(null);
  const [brushColor, setBrushColor] = useState(COLORS.black);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [signatureData, setSignatureData] = useState("");
  const [signatureStatus, setSignatureStatus] = useState<"empty" | "signed">(
    "empty"
  );
  const previousOpenedRef = useRef(opened);

  if (opened && !previousOpenedRef.current) {
    if (canvasRef.current) {
      setTimeout(() => {
        if (canvasRef.current) {
          canvasRef.current.clear();
          setSignatureData("");
          setSignatureStatus("empty");
        }
      }, 0);
    }
  }
  previousOpenedRef.current = opened;

  const getImg = useCallback((): string => {
    if (canvasRef.current?.canvasContainer.children[1]) {
      return canvasRef.current.canvasContainer.children[1].toDataURL();
    }
    return "";
  }, []);

  const handleClear = useCallback((): void => {
    if (canvasRef.current) {
      canvasRef.current.clear();
      setSignatureData("");
      setSignatureStatus("empty");
    }
  }, []);

  const handleCanvasChange = useCallback((): void => {
    const data = getImg();
    setSignatureData(data);
    setSignatureStatus(data && data.length > 5000 ? "signed" : "empty");
  }, [getImg]);

  const handleSave = useCallback((): void => {
    if (signatureStatus === "signed") {
      onSave(signatureData);
      onClose();
    }
  }, [signatureData, signatureStatus, onSave, onClose]);

  const handleClose = useCallback(() => {
    setSignatureData("");
    setSignatureStatus("empty");
    onClose();
  }, [onClose]);

  const canvasProps = {
    loadTimeOffset: 5,
    lazyRadius: 0,
    brushRadius: 3,
    brushColor,
    catenaryColor: brushColor,
    hideGrid: true,
    canvasWidth: 500,
    canvasHeight: 200,
    disabled: false,
    imgSrc: "",
    saveData: "",
    immediateLoading: false,
    hideInterface: false,
    className: "canvas",
    onChange: handleCanvasChange,
  };

  return (
    <Modal
      opened={opened}
      onClose={handleClose}
      title="Draw Your Signature"
      size="lg"
      centered
    >
      <Paper>
        <Text c={COLORS.dimmed} ta="center" size="sm" mb="md">
          Please draw your signature below
        </Text>

        <Box
          style={{
            border: "1px dashed",
            borderRadius: "4px",
            padding: "10px",
          }}
        >
          <Center>
            <CanvasDraw
              {...canvasProps}
              ref={canvasRef as React.RefObject<CanvasDraw>}
            />
          </Center>
        </Box>

        <Group align="center" my="md">
          <Popover
            opened={showColorPicker}
            onChange={setShowColorPicker}
            position="bottom"
            withArrow
            shadow="md"
          >
            <Popover.Target>
              <Button
                leftSection={<IconPalette size={18} />}
                variant="light"
                onClick={() => setShowColorPicker((s) => !s)}
                style={{
                  backgroundColor: brushColor,
                  color:
                    brushColor === COLORS.white ? COLORS.black : COLORS.white,
                }}
                size="sm"
              >
                Ink Color
              </Button>
            </Popover.Target>
            <Popover.Dropdown>
              <GithubPicker
                triangle="hide"
                color={brushColor}
                colors={inkColors}
                width={`${Math.ceil(inkColors.length / 2) * 32}px`}
                onChangeComplete={(c: ColorResult) => {
                  setBrushColor(c.hex);
                  setShowColorPicker(false);
                }}
              />
            </Popover.Dropdown>
          </Popover>

          <Tooltip label="Undo">
            <ActionIcon
              variant="light"
              color={COLORS.blue}
              size="lg"
              onClick={() => canvasRef.current?.undo()}
            >
              <IconArrowBackUp size={20} />
            </ActionIcon>
          </Tooltip>

          <Tooltip label="Clear Signature">
            <ActionIcon
              variant="light"
              color={COLORS.red}
              size="lg"
              onClick={handleClear}
            >
              <IconTrash size={20} />
            </ActionIcon>
          </Tooltip>
        </Group>

        {signatureStatus === "signed" && (
          <Box mt="md" mb="md">
            <Text size="sm" fw={500} c={COLORS.blue} mb="xs">
              Signature Preview:
            </Text>
            <Center>
              <Image
                src={signatureData}
                alt="Signature"
                w="auto"
                h={100}
                fit="contain"
                bg={COLORS.white}
              />
            </Center>
          </Box>
        )}

        <Group justify="flex-end" mt="lg">
          <Button variant="light" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            leftSection={<IconCheck size={18} />}
            onClick={handleSave}
            disabled={signatureStatus !== "signed"}
            color={COLORS.blue}
          >
            Save Signature
          </Button>
        </Group>
      </Paper>
    </Modal>
  );
};

export default DrawSignatureModal;
