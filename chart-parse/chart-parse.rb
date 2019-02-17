#!/usr/bin/ruby

require 'test/unit' 

##先写测试：
class BottomUpChartParserTest < Test::Unit::TestCase
  def test_the_large_can_can_hold_the_water
    # define the sentence to be parsered
    sentence = 'The large can can hold the water'

    # define the dictionary
    dictionary = {
      'the'   => ['ART'],
      'large' => ['ADJ'],
      'can'   => ['N', 'AUX', 'V'],
      'hold'  => ['N', 'V'],
      'water' => ['N', 'V']
    }

    # define the grammars
    grammars = {
      'S'   => ['NP VP'],
      'NP'  => ['ART ADJ N', 'ART N', 'ADJ N'],
      'VP'  => ['AUX VP', 'V NP']
    }

    # define the expected result
    expected_result = ['ART', 'ADJ', 'N', 'AUX', 'V', 'ART', 'N']

    #创建解析类的对象
    parser = BottomUpChartParser.new(dictionary, grammars)
    #解析句子
    flag = parser.parse(sentence)

    puts
    parser.result[0].get_step()

    assert flag #确认返回的flag为真
    assert parser.result.length == 1 #确认返回结果的长度为1
#    assert_equal expected_result, parser.result[0].get_step() #确认返回结果与期望结果相同
  end
end

class Tree
  attr_accessor :key, :data, :children, :children_hash
  attr_accessor :parent, :is_root

  def initialize key, data
    @key = key
    @data = data
    @children = []
    @children_hash = {}
    @is_root = true
    @parent = nil
  end

  def add_child child
    @children << child
    @children_hash.store child.key, child
    child.parent = self
    child.is_root = false
    child
  end

  def get_leaves
    #puts "#{children}"
    #p @children_hash
    children_hash.each{|k,v| p "#{k} -> #@v"}

#    @node = self.children
#    while @node
#        #p node
#        childhash = @node.children_hash
#        childhash.each{|k,v| p "#{k} -> #@v"}
#        unless children.nil?
#            @node = @node.children
#        else
#            break
#        end
#    end
  end

  def is_root?
    @is_root
  end
end

##定义成分，成分中有一棵树，用来记录整个分析的过程：
class Constituent
    #定义类的成员
    attr_accessor :start, :end, :value, :root #attr_accessor标示这些变量是公有可访问的的

    #构造函数，初始化一棵树
    def initialize start_index, end_index, value, history
        @start = start_index
        @end = end_index
        @value = value
        @history = history

        #构造一个Tree
        @root = Tree.new(value,
        {
            :grammar => @value,
            :start => @start,
            :end => @end
        })

        #
        return @history.each() { |child| @root.add_child(child) }
    end

    #返回树的所有叶子节点
    def get_step
        return @root.get_leaves
    end
end

##定义边：
class Arc
    #定义类的成员
    attr_reader :start, :end, :applied_grammar, :position

    #构造函数
    def initialize(start_index, end_index, applied_grammar, parent_grammar, position, history)
        @start = start_index
        @end = end_index
        @applied_grammar = applied_grammar
        @parent = parent_grammar
        @position = position
        @grammars = applied_grammar.split()
        @history = []
        @history.concat(history)
    end

    #当前位置有没有达到句子结束
    def is_active?
        return @position < @grammars.length
    end

    #该活动边的当前位置是否与成分匹配
    def is_next? constituent
        return @grammars[@position] == constituent.value &&
            ((@end == constituent.start && @position != 0) ||
             (@start == constituent.start && @end == constituent.end && @position == 0))
    end

    def extend_arc constituent
        raise(ArgumentError, '') unless is_next?(constituent)

        return Arc.new(@start, constituent.end, @applied_grammar, @parent, @position + 1, @history + [constituent.root])
    end

    def create_next_consitutent
        return Constituent.new(@start, @end, @parent, @history)
    end

    def to_s
        desc = '(('
        @grammars.each_with_index { |g, index|
            desc << '•' if index == @position
            desc << g << ' '
        }
        desc.chop!
        desc << '•' if @position >= @grammars.length
        desc << '), ' << @start.to_s() << ', ' << @end.to_s() << ')'
        desc
    end
end

##定义分析器：
class BottomUpChartParser
    #定义类的成员
    attr_reader :result

    #构造函数（字典表，语法表）
    def initialize dictionary, grammars
        raise(ArgumentError, 'The dictionary or grammars can not be nil.') if dictionary.nil? || grammars.nil?

        #初始化字典和语法表
        @dictionary = dictionary
        @grammars = grammars
    end

    # 解析句子
    def parse sentence
        raise(ArgumentError, '') if sentence.nil? || sentence.strip().empty?
        @index = 0
        @agenda = []
        @result = []
        @chart = {}
        @step = 1
        @words = sentence.downcase().split() #1.将句子转小写，再切分成一个个的单词
        while add_word_to_agenda             #2.将一个单词放到代理表中
            handle_agenda                    #3.处理代理表
        end

        return !@result.empty?
    end

    # Look up the interpretations for the next word and add them to the agenda.
    def add_word_to_agenda
        return false if @index >= @words.length

        #获取当前单词，并检查其是否包含在字典当中
        current_word = @words[@index]
        return false unless @dictionary.has_key?(current_word)

        #根据单词遍历字典，查单词的词性
        for item in @dictionary[current_word]
            #根据单词的每个词性，生成成分，并放到待处理表agenda中
            @agenda << Constituent.new(@index, @index + 1, item, [])
        end

        @index += 1
        return true
    end

    #处理待处理表
    def handle_agenda
        return if @agenda.empty?

        #从待处理表中取出各个成分
        temp_agenda = [].concat(@agenda)
        @agenda.clear

        for constituent in temp_agenda
            p "Step#{@step} - Input constituent: ((#{constituent.value}), #{constituent.start}, #{constituent.end})"
 
            #如果该成分覆盖到了整个句子，将其放入result中
            @result << constituent if is_success(constituent)

            #创建边
            @chart.merge!(create_arc_begin_with(constituent))

            #扩展边
            extend_arc constituent
            @step += 1
        end

        handle_agenda
    end

    # 如果某个成分正好对应着到整个句子，解析成功
    def is_success(constituent)
        if constituent.start == 0 && constituent.end == @words.length
            return true
        else
            return false
        end
    end

    def create_arc_begin_with(constituent)
        match_grammars = {}
        result = {}

        @grammars.each() { |key, value| 
            match_grammars.store(key, [])

            #在语法表中查找：与成分值一样或以成分值开始的语法
            match_grammars[key].concat value.find_all { |grammar|
                grammar == constituent.value ||
                grammar.start_with?(constituent.value + ' ') }
        }

        #将匹配到的语法生成新的活动边
        match_grammars.each { |key, value|
            value.each() { |g|
                arc = Arc.new(constituent.start, constituent.end, g, key, 0, [])

                result.store(arc.to_s(), arc) unless result.has_key?(arc.to_s())
                p "\s\sAdd new arc to chart: #{arc.to_s()}"
            }
        }
        return result
    end

    # arc extension
    def extend_arc(constituent)
	#找到当前所有活动边
        temp_chart = @chart.values.find_all() { |arc| arc.is_active? }

        #找到下一个成分等于当前成分的所有活动边
        for arc in temp_chart
            #p arc.to_s
            #p consitutent

            if arc.is_next?(constituent)
                #扩展当前位置与成分匹配的活动边
                new_arc = arc.extend_arc(constituent)
                p "\s\sAdd extended arc: #{new_arc.to_s()}"

                #将扩展后的活动边加入线图中
                @chart.store(new_arc.to_s(), new_arc) unless @chart.has_key?(new_arc.to_s())

                #将扩展后的非活动边生成新的成分
                unless (new_arc.is_active?)
                    new_constituent = new_arc.create_next_consitutent()
                    p "\s\sAdd new constituent: ((#{new_constituent.value}), #{new_constituent.start}, #{new_constituent.end})"

                    #将新的成分放入待处理表中
                    @agenda << new_constituent
                end
            end
         end
    end
end

