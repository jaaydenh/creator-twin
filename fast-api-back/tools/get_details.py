from models.personality import Verbal
from tools.transcript import get_transcript,split_text
from tools.extract_details import get_chain
from langchain_core.output_parsers import PydanticOutputParser



def get_personality(video_id:list[str]):

    """
    Get the personality of the person in the video
    Args:
        video_id: The id of the video
    Returns:
        The personality of the person in the video
    """
    script=get_transcript(video_id)
    parser = PydanticOutputParser(pydantic_object=Verbal)
    texts=split_text(script)
    chain=get_chain()
    result = chain.invoke({
        "format_instructions": parser.get_format_instructions(),
        "length": len(texts)
    })
    result=result['messages'][-1].content
    return str(parser.parse(result).model_dump())