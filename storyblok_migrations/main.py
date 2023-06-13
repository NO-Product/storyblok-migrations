from datetime import datetime
from enum import Enum

import requests


class StoryblokServer(str, Enum):
    EU = "https://mapi.storyblok.com"
    US = "https://api-us.storyblok.com"
    CN = "https://app.storyblokchina.cn"


def _request(*args, **kwargs):
    response = requests.request(*args, **kwargs)
    response.raise_for_status()
    return response.json()


def fetchBlocks(spaceId: str, pat: str, baseUrl=StoryblokServer.US):
    endpoint = f"{baseUrl}/v1/spaces/{spaceId}/components/"
    return _request("GET", endpoint, headers={"Authorization": pat})


def createBlock(spaceId: str, pat: str, block: dict, baseUrl=StoryblokServer.US):
    endpoint = f"{baseUrl}/v1/spaces/{spaceId}/components/"
    return _request("POST", endpoint, json=block, headers={"Authorization": pat})


def updateBlock(
    spaceId: str, pat: str, blockId: str, block: dict, baseUrl=StoryblokServer.US
):
    endpoint = f"{baseUrl}/v1/spaces/{spaceId}/components/{blockId}"
    return _request("PUT", endpoint, json=block, headers={"Authorization": pat})


def migrateBlocksIndividual(
    spaceIdSource: str,
    patSource: str,
    spaceIdTarget: str,
    patTarget: str,
    blockName: str,
    includeChildBlocks: bool,
    baseUrlSource=StoryblokServer.US,
    baseUrlTarget=StoryblokServer.US,
):
    blocksSource = fetchBlocks(spaceIdSource, patSource, baseUrl=baseUrlSource)
    blocksTarget = fetchBlocks(spaceIdTarget, patTarget, baseUrl=baseUrlTarget)

    return _migrateBlocksIndividual(
        blocksSource=blocksSource,
        blocksTarget=blocksTarget,
        spaceIdSource=spaceIdSource,
        patSource=patSource,
        spaceIdTarget=spaceIdTarget,
        patTarget=patTarget,
        blockName=blockName,
        includeChildBlocks=includeChildBlocks,
        baseUrlSource=baseUrlSource,
        baseUrlTarget=baseUrlTarget,
    )


def _migrateBlocksIndividual(
    blocksSource: dict,
    blocksTarget: dict,
    spaceIdSource: str,
    patSource: str,
    spaceIdTarget: str,
    patTarget: str,
    blockName: str,
    includeChildBlocks: bool,
    baseUrlSource=StoryblokServer.US,
    baseUrlTarget=StoryblokServer.US,
):
    blockSource = findBlockByName(blockName, blocksSource)
    if not blockSource:
        raise Exception(f"Source block '{blockName}' not found")

    if includeChildBlocks:
        nestedBlocks = getNestedBlocks(blocksSource, blockSource)
        for nestedBlock in nestedBlocks:
            _migrateBlocksIndividual(
                blocksSource=blocksSource,
                blocksTarget=blocksTarget,
                spaceIdSource=spaceIdSource,
                patSource=patSource,
                spaceIdTarget=spaceIdTarget,
                patTarget=patTarget,
                blockName=nestedBlock["name"],
                includeChildBlocks=includeChildBlocks,
                baseUrlSource=baseUrlSource,
                baseUrlTarget=baseUrlTarget,
            )

    blockTarget = findBlockByName(blockName, blocksTarget)
    if not blockTarget:
        createBlock(spaceIdTarget, patTarget, blockSource, baseUrl=baseUrlTarget)
    else:
        updateBlock(
            spaceIdTarget,
            patTarget,
            blockTarget["id"],
            blockSource,
            baseUrl=baseUrlTarget,
        )


def getNestedBlocks(allBlocks: dict, block: dict):
    childBlocks = []
    for field_name, field_schema in block["schema"].items():
        if field_schema["type"] == "bloks" and field_schema.get("restrict_components"):
            childBlocks.extend(field_schema["component_whitelist"])
    childBlocks = list(set(childBlocks))
    childBlocks = [
        {
            "name": blockName,
            "nestedTypes": getNestedBlocks(
                allBlocks,
                findBlockByName(blockName, allBlocks),
            ),
        }
        for blockName in childBlocks
    ]
    return childBlocks


def findBlockByName(blockName: str, allBlocks: dict):
    return next(
        filter(lambda block: block["name"] == blockName, allBlocks["components"]), None
    )


def parseStoryblokDate(date: str):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
