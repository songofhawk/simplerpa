from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.action.ActionImage import ActionImage
from simplerpa.core.data.ScreenRect import ScreenRect
from simplerpa.core.detection.Detection import Detection


class OcrDetection(Detection):
    """
    文本检测，在当前页面的指定范围内，首先用OCR识别文字，查找是否与给定文本匹配。如果识别文本和给定文本的匹配度，大于给定值，则认为找到了，并且将其返回

    Example:
        ```yaml
        # State的一个属性
        ocr:
            snapshot: !rect l:75, r:137, t:129, b:157
            text: "看日志"
        ```

    Attributes:
        snapshot (ScreenRect): 屏幕截图位置，限定查找范围，可以指定得大一些，程序会在指定范围内查找图像
        text (str): 要查找的文本字符串
        confidence (float): 置信度，查找文本的时候，并不需要严格一致，程序会模糊匹配，并返回一个置信度（0 ~ 1之间的一个数值），置信度大于给定的数值，才会认为找到了

    ```yaml
    result: 如果找到了，就返回OCR识别的文本本身，如果没有找到，就返回None
    ```
    """

    snapshot: ScreenRect
    text: str
    confidence: float = 0.8

    def do_detection(self, find_all=False):
        image_current = ActionScreen.snapshot(self.snapshot.evaluate())
        confidence, text = self.text_similar(self.text, image_current)
        if confidence >= self.confidence:
            return text
        else:
            return None

    def text_similar(self, source_text, target_pillow_image):
        """
        检查指定图像中是否包含特定的文字
        :param source_text: 要查找的文字
        :param target_pillow_image: 目标图像，函数将从这个图像提取文字，
        :return:相似度，完全相同是1，完全不同是0，其他是 source_text 与识别出来的文字的比例
        """

        if len(source_text) == 0:
            '''如果source_text是空字符，就认为永远能识别不出来'''
            return 0, None

        cv_image = ActionImage.pil_to_cv(target_pillow_image)
        ActionImage.log_image('target', cv_image, debug=self.debug)
        text_from_image = ActionImage.ocr(cv_image, debug=self.debug)

        if source_text in text_from_image:
            return len(source_text) / len(text_from_image), text_from_image
        else:
            return 0, None
