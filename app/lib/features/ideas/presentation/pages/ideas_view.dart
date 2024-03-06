import 'package:band_app/core/constants/palette.dart';
import 'package:band_app/features/ideas/domain/usecases/get_ideas.dart';
import 'package:band_app/features/ideas/presentation/bloc/ideas/ideas_bloc.dart';
import 'package:band_app/features/ideas/presentation/bloc/ideas/ideas_event.dart';
import 'package:band_app/features/ideas/presentation/bloc/ideas/ideas_state.dart';
import 'package:band_app/features/ideas/presentation/widgets/idea.dart';
import 'package:band_app/injection_container.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

class IdeasView extends StatefulWidget{
  const IdeasView({super.key});

  @override
  State<IdeasView> createState() => _IdeasViewState();
}

class _IdeasViewState extends State<IdeasView> {

  @override
  void initState() {
    context.read<IdeasBloc>().add(const IdeasLoaded());
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return _buildBody(context);
  }

  Widget _buildBody(BuildContext context) {
    return BlocConsumer<IdeasBloc, IdeasState>(
      builder: (BuildContext context, IdeasState state) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              Expanded(
                child: ListView.separated (
                  itemCount: state.ideas.length,
                  itemBuilder: (BuildContext context, int index) {
                    return IdeaWidget(idea: state.ideas[index]);
                  }, separatorBuilder: (BuildContext context, int index) {
                    return const SizedBox(height: 10);
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: ElevatedButton(
                  style: ButtonStyle(
                    backgroundColor: MaterialStateProperty.all(Palette.dark),
                    fixedSize: MaterialStateProperty.all(Size(MediaQuery.of(context).size.width - 40, 50)),
                    shape: MaterialStateProperty.all(
                        const RoundedRectangleBorder(
                            borderRadius: BorderRadius.all(Radius.circular(5)
                            ))),
                  ),
                  onPressed: (){
                    GoRouter.of(context).pushNamed("create-idea");
                  },
                  child: const Icon(Icons.add, color: Palette.yellow, size: 32,),
                ),
              ),
            ],
          ),
        );
      }, listener: (BuildContext context, IdeasState state) {
        if (state is IdeasVoteFailure){
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              behavior: SnackBarBehavior.floating,
              content: Text(state.message),
            ),
          );
        }
     },
    );
  }
}