local audience = ""

function Meta(meta)
  if meta.audience ~= nil then
    audience = pandoc.utils.stringify(meta.audience)
  elseif meta.visibility_mode ~= nil then
    audience = pandoc.utils.stringify(meta.visibility_mode)
  end
  return meta
end

local function active_audience()
  if audience ~= "" then
    return audience
  end
  if quarto ~= nil and quarto.doc ~= nil and quarto.doc.metadata ~= nil then
    if quarto.doc.metadata.audience ~= nil then
      return pandoc.utils.stringify(quarto.doc.metadata.audience)
    end
    if quarto.doc.metadata.visibility_mode ~= nil then
      return pandoc.utils.stringify(quarto.doc.metadata.visibility_mode)
    end
  end
  return ""
end

local function should_drop(classes)
  local active = active_audience()
  for _, class_name in ipairs(classes) do
    if class_name == "teacher-only" and active == "student" then
      return true
    end
    if class_name == "student-only" and active == "teacher" then
      return true
    end
  end
  return false
end

function Div(element)
  if should_drop(element.classes) then
    return {}
  end
  return element
end

function Span(element)
  if should_drop(element.classes) then
    return {}
  end
  return element
end
