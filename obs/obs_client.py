import obsws_python as obs


class OBSClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 4455,
        password: str = "",
    ) -> None:
        self.host = host
        self.port = port
        self.password = password

        self.client = None

    def connect(self) -> None:
        self.client = obs.ReqClient(
            host=self.host,
            port=self.port,
            password=self.password,
            timeout=3,
        )

        print("🟢 Connected to OBS")

    def disconnect(self) -> None:
        if self.client is not None:
            self.client.disconnect()
            self.client = None

        print("🔴 Disconnected from OBS")

    def get_scene_list(self):
        if self.client is None:
            raise RuntimeError("OBS is not connected.")

        return self.client.get_scene_list()

    def set_source_visibility(
        self,
        scene_name: str,
        source_name: str,
        visible: bool,
    ) -> None:
        if self.client is None:
            raise RuntimeError("OBS is not connected.")

        item = self.client.get_scene_item_id(
            scene_name,
            source_name,
        )

        self.client.set_scene_item_enabled(
            scene_name,
            item.scene_item_id,
            visible,
        )

        state = "visible" if visible else "hidden"

        print(f"👁️ {source_name}: {state}")
